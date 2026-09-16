const assert = require("node:assert/strict");
const http = require("node:http");
const { test } = require("node:test");
const { v5 } = require("uuid");

test("UUID v5 rejects undersized output buffers without partial writes", () => {
  const output = new Uint8Array(8).fill(0xaa);
  assert.throws(() => v5("x", v5.DNS, output, 4), RangeError);
  assert.deepEqual([...output], Array(8).fill(0xaa));
});

test("UUID v5 preserves stable document identifier generation", () => {
  assert.equal(
    v5("www.example.com", v5.DNS),
    "2ed6657d-e927-568b-95e1-2665a8aea6a2",
  );
});

test("the compiled CommonJS SDK sends document queries through its HTTP client", async (t) => {
  const { r2rClient } = require("../dist/index.js");
  let request;
  const server = http.createServer((req, res) => {
    request = { method: req.method, url: new URL(req.url, "http://localhost") };
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ results: [], total_entries: 0 }));
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(() => new Promise((resolve) => server.close(resolve)));
  const client = new r2rClient(
    `http://127.0.0.1:${server.address().port}`,
    false,
  );
  const result = await client.documents.list({ limit: 2, ownerOnly: true });
  assert.equal(request.method, "GET");
  assert.equal(request.url.pathname, "/v3/documents");
  assert.equal(request.url.searchParams.get("limit"), "2");
  assert.equal(request.url.searchParams.get("owner_only"), "true");
  assert.deepEqual(result.results, []);
});
