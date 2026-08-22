#!/usr/bin/env node

"use strict";

const childProcess = require("node:child_process");
const crypto = require("node:crypto");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");

const HTTP_METHODS = [
  "get",
  "put",
  "post",
  "delete",
  "options",
  "head",
  "patch",
  "trace",
];

function usage() {
  return `Usage:
  redoc-pr-visuals.sh --before <openapi> --after <openapi> --output-dir <dir> [options]

Options:
  --endpoint "METHOD /path"  Capture only this changed endpoint. Repeatable.
  --plan-only                Detect changes without rendering or screenshots.
  --keep-temp                Preserve temporary bundled HTML for debugging.
  --help                     Show this help.

The command writes capture-plan.json, pr-section.md, and one PNG for every
non-empty before/after cell. It provisions pinned Redocly and Playwright
packages in a user cache; no project dependency or global install is required.`;
}

function fail(message) {
  throw new Error(message);
}

function parseArgs(argv) {
  const options = {
    before: null,
    after: null,
    outputDir: null,
    endpoints: [],
    planOnly: false,
    keepTemp: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    const next = () => {
      index += 1;
      if (index >= argv.length) fail(`${token} requires a value`);
      return argv[index];
    };

    if (token === "--before") options.before = next();
    else if (token === "--after") options.after = next();
    else if (token === "--output-dir") options.outputDir = next();
    else if (token === "--endpoint") options.endpoints.push(next());
    else if (token === "--plan-only") options.planOnly = true;
    else if (token === "--keep-temp") options.keepTemp = true;
    else if (token === "--help" || token === "-h") {
      console.log(usage());
      process.exit(0);
    } else fail(`unknown argument: ${token}`);
  }

  for (const key of ["before", "after", "outputDir"]) {
    if (!options[key]) fail(`--${key === "outputDir" ? "output-dir" : key} is required`);
  }

  options.before = path.resolve(options.before);
  options.after = path.resolve(options.after);
  options.outputDir = path.resolve(options.outputDir);
  for (const specPath of [options.before, options.after]) {
    if (!fs.statSync(specPath, { throwIfNoEntry: false })?.isFile()) {
      fail(`OpenAPI file does not exist: ${specPath}`);
    }
  }
  return options;
}

function run(executable, args) {
  const result = childProcess.spawnSync(executable, args, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
  if (result.status !== 0) {
    process.stderr.write(result.stdout || "");
    process.stderr.write(result.stderr || "");
    fail(`${path.basename(executable)} failed with exit code ${result.status}`);
  }
  return result.stdout;
}

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, canonicalize(value[key])]),
    );
  }
  return value;
}

function stable(value) {
  return JSON.stringify(canonicalize(value));
}

function operationKey(method, apiPath) {
  return `${method.toUpperCase()} ${apiPath}`;
}

function generatedOperationId(method, apiPath) {
  const stem = `${method}-${apiPath}`
    .toLowerCase()
    .replace(/[{}]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "") || "operation";
  const digest = crypto
    .createHash("sha1")
    .update(operationKey(method, apiPath))
    .digest("hex")
    .slice(0, 8);
  return `aburasashi-${stem}-${digest}`;
}

function slug(value) {
  return value
    .replace(/([a-z0-9])([A-Z])/g, "$1-$2")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function ensureOperationIds(spec) {
  const operations = new Map();
  const seenIds = new Set();
  for (const [apiPath, pathItem] of Object.entries(spec.paths || {})) {
    if (!pathItem || typeof pathItem !== "object") continue;
    for (const method of HTTP_METHODS) {
      const operation = pathItem[method];
      if (!operation || typeof operation !== "object") continue;
      const key = operationKey(method, apiPath);
      const operationId = operation.operationId || generatedOperationId(method, apiPath);
      if (seenIds.has(operationId)) fail(`duplicate operationId: ${operationId}`);
      seenIds.add(operationId);
      operation.operationId = operationId;
      const parameters = new Map();
      for (const rawParameter of [
        ...(pathItem.parameters || []),
        ...(operation.parameters || []),
      ]) {
        const parameter = resolveNode(spec, rawParameter) || rawParameter;
        const parameterKey =
          parameter.name && parameter.in
            ? `${parameter.in}:${parameter.name}`
            : stable(rawParameter);
        parameters.set(parameterKey, rawParameter);
      }
      operations.set(key, {
        key,
        method: method.toUpperCase(),
        path: apiPath,
        operation: { ...operation, parameters: [...parameters.values()] },
        operationId,
        title: operation.summary || operation.operationId,
      });
    }
  }
  return operations;
}

function jsonPointer(spec, ref) {
  if (!ref.startsWith("#/")) return null;
  let current = spec;
  for (const part of ref
    .slice(2)
    .split("/")
    .map((item) => item.replace(/~1/g, "/").replace(/~0/g, "~"))) {
    current = current?.[part];
  }
  return current || null;
}

function resolveNode(spec, node, seenRefs = new Set()) {
  if (!node || typeof node !== "object" || !node.$ref) return node;
  if (seenRefs.has(node.$ref)) return { $circularRef: node.$ref };
  const target = jsonPointer(spec, node.$ref);
  if (!target) return node;
  const nextSeen = new Set(seenRefs);
  nextSeen.add(node.$ref);
  const resolved = resolveNode(spec, target, nextSeen);
  const siblings = Object.fromEntries(
    Object.entries(node).filter(([key]) => key !== "$ref"),
  );
  return { ...resolved, ...siblings };
}

function schemaSignature(spec, schema, required, seenRefs = new Set()) {
  const resolved = resolveNode(spec, schema, seenRefs) || {};
  const result = { required };
  for (const [key, value] of Object.entries(resolved)) {
    if (key === "$ref" || key === "properties") continue;
    if (["allOf", "oneOf", "anyOf"].includes(key) && Array.isArray(value)) {
      result[key] = value.map((item) => schemaSignature(spec, item, false, seenRefs));
    } else if (key === "items" && value && typeof value === "object") {
      result.items = schemaSignature(spec, value, false, seenRefs);
    } else {
      result[key] = value;
    }
  }
  return canonicalize(result);
}

function hasExpandableProperties(spec, rawSchema, seenRefs = new Set()) {
  if (!rawSchema || typeof rawSchema !== "object") return false;
  let schema = rawSchema;
  const nextSeen = new Set(seenRefs);
  if (rawSchema.$ref) {
    if (seenRefs.has(rawSchema.$ref)) return false;
    const target = jsonPointer(spec, rawSchema.$ref);
    if (!target) return false;
    nextSeen.add(rawSchema.$ref);
    schema = {
      ...target,
      ...Object.fromEntries(
        Object.entries(rawSchema).filter(([key]) => key !== "$ref"),
      ),
    };
  }
  if (schema.properties && Object.keys(schema.properties).length) return true;
  if (hasExpandableProperties(spec, schema.items, nextSeen)) return true;
  return ["allOf", "oneOf", "anyOf"].some(
    (keyword) =>
      Array.isArray(schema[keyword]) &&
      schema[keyword].some((branch) =>
        hasExpandableProperties(spec, branch, nextSeen),
      ),
  );
}

function collectOperationSchemaInfo(spec, operation, includeErrors) {
  const entries = new Map();
  const objectFields = new Map();

  function visitSchema(rawSchema, prefix, seenRefs = new Set()) {
    if (!rawSchema || typeof rawSchema !== "object") return;
    const ref = rawSchema.$ref;
    if (ref && seenRefs.has(ref)) return;
    const nextSeen = new Set(seenRefs);
    if (ref) nextSeen.add(ref);
    const schema = resolveNode(spec, rawSchema, seenRefs) || {};

    for (const keyword of ["allOf", "oneOf", "anyOf"]) {
      if (Array.isArray(schema[keyword])) {
        for (const branch of schema[keyword]) visitSchema(branch, prefix, nextSeen);
      }
    }
    if (schema.items) visitSchema(schema.items, `${prefix}[]`, nextSeen);

    const properties = schema.properties;
    if (!properties || typeof properties !== "object") return;
    const requiredNames = new Set(Array.isArray(schema.required) ? schema.required : []);
    for (const [name, child] of Object.entries(properties)) {
      const propertyPath = `${prefix}.${name}`;
      entries.set(propertyPath, {
        path: propertyPath,
        name,
        signature: schemaSignature(spec, child, requiredNames.has(name), nextSeen),
      });
      if (hasExpandableProperties(spec, child, nextSeen)) {
        objectFields.set(propertyPath, { path: propertyPath, name });
      }
      visitSchema(child, propertyPath, nextSeen);
    }
  }

  for (const rawParameter of operation.parameters || []) {
    const parameter = resolveNode(spec, rawParameter) || {};
    if (!parameter.name || !parameter.schema) continue;
    const parameterPath = `parameter.${parameter.name}`;
    entries.set(parameterPath, {
      path: parameterPath,
      name: parameter.name,
      signature: schemaSignature(spec, parameter.schema, Boolean(parameter.required)),
    });
    visitSchema(parameter.schema, parameterPath);
  }

  const requestBody = resolveNode(spec, operation.requestBody) || {};
  const requestContent = requestBody.content || {};
  for (const [mediaType, media] of Object.entries(requestContent)) {
    visitSchema(media?.schema, `request.${mediaType}`);
  }

  for (const [status, rawResponse] of Object.entries(operation.responses || {})) {
    const errorResponse =
      status.toLowerCase() === "default" ||
      /^[45]/.test(status) ||
      /^[45]xx$/i.test(status);
    if (!includeErrors && errorResponse) continue;
    const response = resolveNode(spec, rawResponse) || {};
    for (const [mediaType, media] of Object.entries(response.content || {})) {
      visitSchema(media?.schema, `response.${status}.${mediaType}`);
    }
  }

  return { entries, objectFields };
}

function operationFingerprint(spec, operation) {
  const schemaInfo = collectOperationSchemaInfo(spec, operation, true);
  return stable({
    operation,
    schemas: [...schemaInfo.entries.entries()].map(([key, value]) => [
      key,
      value.signature,
    ]),
  });
}

function propertyDiff(beforeInfo, afterInfo) {
  const changes = [];
  const keys = new Set([...beforeInfo.entries.keys(), ...afterInfo.entries.keys()]);
  for (const key of [...keys].sort()) {
    const before = beforeInfo.entries.get(key);
    const after = afterInfo.entries.get(key);
    if (!before) changes.push({ kind: "added", path: key, name: after.name });
    else if (!after) changes.push({ kind: "removed", path: key, name: before.name });
    else if (stable(before.signature) !== stable(after.signature)) {
      changes.push({ kind: "changed", path: key, name: after.name });
    }
  }
  return changes;
}

function expansionNames(info, changedPaths = null) {
  const names = new Set();
  for (const field of info.objectFields.values()) {
    if (
      !changedPaths ||
      changedPaths.some(
        (changedPath) =>
          changedPath === field.path || changedPath.startsWith(`${field.path}.`),
      )
    ) {
      names.add(field.name);
    }
  }
  return [...names].sort();
}

function annotationList(changes, side) {
  const annotations = new Map();
  for (const change of changes) {
    const exists = side === "before" ? change.kind !== "added" : change.kind !== "removed";
    if (!exists) continue;
    const label = change.kind === "removed" ? "REMOVED" : "CHANGE";
    annotations.set(`${change.name}:${label}`, { name: change.name, label });
  }
  return [...annotations.values()];
}

function changedResponseStatuses(changedPaths) {
  const statuses = new Set();
  for (const changedPath of changedPaths) {
    const match = changedPath.match(/^response\.([^.]+)\./);
    if (match) statuses.add(match[1]);
  }
  return [...statuses].sort();
}

function buildPlan(beforeSpec, afterSpec, filters) {
  const beforeOperations = ensureOperationIds(beforeSpec);
  const afterOperations = ensureOperationIds(afterSpec);
  const requested = new Set(
    filters.map((item) => item.trim().replace(/^([a-z]+)/i, (method) => method.toUpperCase())),
  );
  const keys = new Set([...beforeOperations.keys(), ...afterOperations.keys()]);
  const endpoints = [];

  for (const key of [...keys].sort()) {
    if (requested.size && !requested.has(key)) continue;
    const before = beforeOperations.get(key);
    const after = afterOperations.get(key);
    let changeType;
    if (!before) changeType = "added";
    else if (!after) changeType = "removed";
    else if (
      operationFingerprint(beforeSpec, before.operation) !==
      operationFingerprint(afterSpec, after.operation)
    ) {
      changeType = "modified";
    } else continue;

    const includeErrors = changeType === "modified";
    const beforeInfo = before
      ? collectOperationSchemaInfo(beforeSpec, before.operation, includeErrors)
      : { entries: new Map(), objectFields: new Map() };
    const afterInfo = after
      ? collectOperationSchemaInfo(afterSpec, after.operation, includeErrors)
      : { entries: new Map(), objectFields: new Map() };
    const properties =
      changeType === "modified" ? propertyDiff(beforeInfo, afterInfo) : [];
    const changedPaths = properties.map((item) => item.path);
    const representative = after || before;
    const fileStem = slug(representative.operationId || `${representative.method}-${representative.path}`);

    const beforeAnnotations = annotationList(properties, "before");
    const afterAnnotations = annotationList(properties, "after");
    endpoints.push({
      key,
      method: representative.method,
      path: representative.path,
      title: representative.title,
      changeType,
      fileStem,
      properties,
      before: before
        ? {
            operationId: before.operationId,
            expand:
              changeType === "modified"
                ? expansionNames(beforeInfo, changedPaths)
                : [],
            annotations: beforeAnnotations,
            responseStatuses: changedResponseStatuses(changedPaths),
            expandAllProperties: false,
            rootLabel:
              changeType === "removed"
                ? "REMOVED"
                : changeType === "modified" && beforeAnnotations.length === 0
                  ? "CHANGE"
                  : null,
            missingRemoved: [],
            image: `${fileStem}-before.png`,
          }
        : null,
      after: after
        ? {
            operationId: after.operationId,
            expand:
              changeType === "added"
                ? expansionNames(afterInfo)
                : expansionNames(afterInfo, changedPaths),
            annotations: afterAnnotations,
            responseStatuses: changedResponseStatuses(changedPaths),
            expandAllProperties: changeType === "added",
            rootLabel:
              changeType === "modified" && afterAnnotations.length === 0
                ? "CHANGE"
                : null,
            missingRemoved: properties
              .filter((item) => item.kind === "removed")
              .map((item) => item.name),
            image: `${fileStem}-after.png`,
          }
        : null,
    });
  }

  if (requested.size) {
    const found = new Set(endpoints.map((item) => item.key));
    const missing = [...requested].filter((item) => !found.has(item));
    if (missing.length) {
      fail(`requested endpoint is not changed or does not exist: ${missing.join(", ")}`);
    }
  }
  if (!endpoints.length) fail("no changed OpenAPI endpoints were detected");
  return { version: 1, endpoints };
}

function bundleSpec(label, inputPath, temporaryDir, redoclyBin) {
  const outputPath = path.join(temporaryDir, `${label}.json`);
  run(redoclyBin, ["bundle", inputPath, "--output", outputPath, "--ext", "json"]);
  const spec = JSON.parse(fs.readFileSync(outputPath, "utf8"));
  ensureOperationIds(spec);
  fs.writeFileSync(outputPath, `${JSON.stringify(spec, null, 2)}\n`);
  return { spec, outputPath };
}

function buildDocs(label, bundledPath, temporaryDir, redoclyBin) {
  const htmlPath = path.join(temporaryDir, `${label}.html`);
  run(redoclyBin, [
    "build-docs",
    bundledPath,
    "--output",
    htmlPath,
    "--disableGoogleFont",
  ]);
  return htmlPath;
}

async function launchHeadlessBrowser(playwrightBin) {
  const requested = process.env.ABURASASHI_REDOC_BROWSER || "auto";
  if (requested === "auto" || requested === "chrome") {
    try {
      return await chromium.launch({ channel: "chrome", headless: true });
    } catch (error) {
      if (requested === "chrome") throw error;
      console.error("System Chrome is unavailable; installing cached Playwright Chromium.");
    }
  }
  if (!fs.existsSync(chromium.executablePath())) {
    const result = childProcess.spawnSync(playwrightBin, ["install", "chromium"], {
      stdio: "inherit",
    });
    if (result.status !== 0) fail("Playwright Chromium installation failed");
  }
  return chromium.launch({ headless: true });
}

async function closeUnrelatedAccordions(root) {
  for (let pass = 0; pass < 20; pass += 1) {
    const buttons = root.locator(
      'button[aria-label^="expand "], button[aria-label^="collapse "]',
    );
    const count = await buttons.count();
    if (!count) return;
    let clicked = false;
    for (let index = count - 1; index >= 0; index -= 1) {
      const button = buttons.nth(index);
      const expanded = await button.evaluate(
        (element) =>
          element.getAttribute("aria-label")?.startsWith("collapse ") ||
          element.closest("tr")?.classList.contains("expanded") ||
          false,
      );
      if (expanded && (await button.isVisible())) {
        await button.click();
        clicked = true;
      }
    }
    if (!clicked) return;
  }
  fail("unable to close ReDoc property accordions deterministically");
}

async function configureRelevantResponses(root, requestedStatuses) {
  const requested = new Set(requestedStatuses || []);
  for (let pass = 0; pass < 50; pass += 1) {
    const buttons = root.locator("button");
    const count = await buttons.count();
    let clicked = false;
    for (let index = 0; index < count; index += 1) {
      const button = buttons.nth(index);
      const strong = button.locator("strong").first();
      if (!(await strong.count())) continue;
      const statusText = (await strong.textContent())?.trim() || "";
      const status = Number.parseInt(statusText, 10);
      const successful = Number.isInteger(status) && status < 400;
      const shouldExpand = successful || requested.has(statusText);
      const expanded = await button.evaluate(
        (element) => (element.parentElement?.children.length || 0) > 1,
      );
      if (
        expanded !== shouldExpand &&
        (await button.isVisible()) &&
        (await button.isEnabled())
      ) {
        await button.click();
        clicked = true;
        break;
      }
    }
    if (!clicked) return;
  }
  fail("unable to configure the relevant ReDoc response panels deterministically");
}

async function expandRequestedProperties(root, names) {
  for (let pass = 0; pass < 30; pass += 1) {
    let clicked = false;
    for (const name of names) {
      const buttons = root.locator(`button[aria-label=${JSON.stringify(`expand ${name}`)}]`);
      const count = await buttons.count();
      if (!count) continue;
      for (let index = 0; index < count; index += 1) {
        const button = buttons.nth(index);
        const expanded = await button.evaluate(
          (element) => element.closest("tr")?.classList.contains("expanded") || false,
        );
        if (!expanded && (await button.isVisible())) {
          await button.click();
          clicked = true;
        }
      }
    }
    if (!clicked) return;
  }
  fail("unable to expand the requested ReDoc property accordions deterministically");
}

async function expandAllVisibleProperties(root) {
  for (let pass = 0; pass < 50; pass += 1) {
    const buttons = root.locator('button[aria-label^="expand "]');
    const count = await buttons.count();
    let clicked = false;
    for (let index = 0; index < count; index += 1) {
      const button = buttons.nth(index);
      const expanded = await button.evaluate(
        (element) => element.closest("tr")?.classList.contains("expanded") || false,
      );
      if (!expanded && (await button.isVisible())) {
        await button.click();
        clicked = true;
      }
    }
    if (!clicked) return;
  }
  fail("unable to expand all ReDoc property accordions deterministically");
}

async function annotate(root, capture) {
  await root.evaluate((element, payload) => {
    const COLORS = {
      CHANGE: { border: "#d97706", background: "#b45309" },
      REMOVED: { border: "#dc2626", background: "#b91c1c" },
    };
    element.style.position = "relative";
    element.style.background = "#ffffff";
    element.style.padding = "32px 24px 24px";
    element.style.boxSizing = "border-box";

    function badge(label) {
      const palette = COLORS[label];
      const markerBadge = document.createElement("span");
      markerBadge.textContent = label;
      Object.assign(markerBadge.style, {
        position: "absolute",
        top: "3px",
        right: "3px",
        padding: "3px 8px",
        borderRadius: "4px",
        background: palette.background,
        color: "#ffffff",
        font: "700 12px/1.4 Arial, sans-serif",
        letterSpacing: "0.08em",
        boxShadow: "0 1px 2px rgba(0, 0, 0, 0.22)",
      });
      return markerBadge;
    }

    function overlay(target, label) {
      const palette = COLORS[label];
      const rootBox = element.getBoundingClientRect();
      const targetBox = target.getBoundingClientRect();
      const marker = document.createElement("div");
      marker.dataset.aburasashiAnnotation = label;
      Object.assign(marker.style, {
        position: "absolute",
        pointerEvents: "none",
        zIndex: "2147483647",
        left: `${targetBox.left - rootBox.left - 3}px`,
        top: `${targetBox.top - rootBox.top - 3}px`,
        width: `${targetBox.width + 6}px`,
        height: `${targetBox.height + 6}px`,
        border: `3px solid ${palette.border}`,
        borderRadius: "6px",
        boxSizing: "border-box",
      });
      marker.appendChild(badge(label));
      element.appendChild(marker);
    }

    if (payload.missingRemoved.length) {
      const banner = document.createElement("div");
      banner.dataset.aburasashiRemoved = "true";
      banner.textContent = `REMOVED: ${payload.missingRemoved.join(", ")}`;
      Object.assign(banner.style, {
        margin: "0 0 20px",
        padding: "10px 14px",
        border: "3px dashed #dc2626",
        borderRadius: "6px",
        background: "#fef2f2",
        color: "#991b1b",
        font: "700 13px/1.4 Arial, sans-serif",
        letterSpacing: "0.04em",
      });
      element.prepend(banner);
    }

    if (payload.rootLabel) {
      const palette = COLORS[payload.rootLabel];
      element.style.boxShadow = `inset 0 0 0 3px ${palette.border}`;
      element.appendChild(badge(payload.rootLabel));
    }
    for (const annotation of payload.annotations) {
      const fields = [...element.querySelectorAll('td[kind="field"][title]')].filter(
        (field) => field.getAttribute("title") === annotation.name,
      );
      for (const field of fields) overlay(field.closest("tr") || field, annotation.label);
    }
  }, capture);
}

async function captureEndpoint(page, htmlPath, capture, outputPath) {
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "load" });
  await page.addStyleTag({
    content: "* { animation: none !important; transition: none !important; }",
  });
  const operation = page.locator(
    `[data-section-id=${JSON.stringify(`operation/${capture.operationId}`)}]`,
  );
  await operation.waitFor({ state: "visible", timeout: 30_000 });
  const leftColumn = operation.locator(":scope > div").first();
  await configureRelevantResponses(leftColumn, capture.responseStatuses);
  await closeUnrelatedAccordions(leftColumn);
  if (capture.expandAllProperties) await expandAllVisibleProperties(leftColumn);
  else await expandRequestedProperties(leftColumn, capture.expand);
  await annotate(leftColumn, capture);
  await leftColumn.screenshot({
    path: outputPath,
    type: "png",
    animations: "disabled",
  });
  const imageSize = fs.statSync(outputPath).size;
  if (imageSize < 1_000) fail(`screenshot is unexpectedly small: ${outputPath}`);
}

function markdownFor(plan) {
  const lines = ["## OpenAPI documentation", ""];
  for (const endpoint of plan.endpoints) {
    const title = `${endpoint.method} ${endpoint.path}`;
    lines.push(`### \`${title}\``, "", "| Before | After |", "| --- | --- |");
    let beforeCell;
    let afterCell;
    if (!endpoint.before) beforeCell = "**EMPTY**";
    else {
      beforeCell = `![Before ReDoc for ${title}]({{UPLOAD:${endpoint.before.image}}})`;
    }
    if (!endpoint.after) afterCell = "**EMPTY REMOVED**";
    else afterCell = `![After ReDoc for ${title}]({{UPLOAD:${endpoint.after.image}}})`;
    lines.push(`| ${beforeCell} | ${afterCell} |`, "");
  }
  return `${lines.join("\n").trimEnd()}\n`;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const redoclyBin = process.env.ABURASASHI_REDOC_BIN;
  const playwrightBin = process.env.ABURASASHI_PLAYWRIGHT_BIN;
  if (!redoclyBin || !fs.existsSync(redoclyBin)) {
    fail("ABURASASHI_REDOC_BIN must point to the provisioned Redocly CLI");
  }
  if (!playwrightBin || !fs.existsSync(playwrightBin)) {
    fail("ABURASASHI_PLAYWRIGHT_BIN must point to the provisioned Playwright CLI");
  }

  fs.mkdirSync(options.outputDir, { recursive: true });
  const temporaryDir = fs.mkdtempSync(path.join(os.tmpdir(), "aburasashi-redoc-"));
  let browser;
  try {
    const beforeBundle = bundleSpec("before", options.before, temporaryDir, redoclyBin);
    const afterBundle = bundleSpec("after", options.after, temporaryDir, redoclyBin);
    const plan = buildPlan(beforeBundle.spec, afterBundle.spec, options.endpoints);
    fs.writeFileSync(
      path.join(options.outputDir, "capture-plan.json"),
      `${JSON.stringify(plan, null, 2)}\n`,
    );
    fs.writeFileSync(path.join(options.outputDir, "pr-section.md"), markdownFor(plan));

    if (!options.planOnly) {
      const beforeHtml = buildDocs(
        "before",
        beforeBundle.outputPath,
        temporaryDir,
        redoclyBin,
      );
      const afterHtml = buildDocs(
        "after",
        afterBundle.outputPath,
        temporaryDir,
        redoclyBin,
      );
      browser = await launchHeadlessBrowser(playwrightBin);
      const page = await browser.newPage({
        viewport: { width: 1440, height: 1200 },
        deviceScaleFactor: 1,
      });
      for (const endpoint of plan.endpoints) {
        if (endpoint.before) {
          await captureEndpoint(
            page,
            beforeHtml,
            endpoint.before,
            path.join(options.outputDir, endpoint.before.image),
          );
        }
        if (endpoint.after) {
          await captureEndpoint(
            page,
            afterHtml,
            endpoint.after,
            path.join(options.outputDir, endpoint.after.image),
          );
        }
      }
    }

    console.log(
      `Created ${plan.endpoints.length} endpoint section(s) in ${options.outputDir}`,
    );
    if (options.keepTemp) console.log(`Temporary files: ${temporaryDir}`);
  } finally {
    if (browser) await browser.close();
    if (!options.keepTemp) fs.rmSync(temporaryDir, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(`error: ${error.message}`);
  process.exit(1);
});
