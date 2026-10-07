# HTML microdata

The example wraps metadata in a `div` with `itemscope` and an `itemtype` pointing
to the FHR schema. Properties use `itemprop`; nested objects introduce an item
scope. Repeated values and empty arrays are preserved through typed containers.

The converter's HTML representation adds `data-fhr-type` annotations (`object`,
`array`, `string`, `integer`, `number`, `boolean`, `null`) to make the original
JSON/YAML mapping recoverable. An array container holds children with
`itemprop="item"`. These are FHR serialization conventions, not a claim that a
generic Schema.org consumer understands FHR properties or these extensions.
HTML values and attribute text must be escaped; command-line strings are data
and are never executed. Unicode and whitespace in typed strings are preserved.

To embed metadata, copy the generated item-scope element into a page:

```bash
fhr-convert examples/example.fhr.json /tmp/example.html
fhr-convert /tmp/example.html /tmp/example.yaml
fhr-validate /tmp/example.yaml
```

The converter also accepts ordinary repeated scalar properties and nested item
scopes, converting schema-defined numeric fields and lists. It rejects missing,
incomplete, or multiple FHR root scopes; legacy examples with flattened nested
properties should be regenerated. Run the converter round-trip and example tests
before changing this representation. The browser microdata download-tool project
is outside this release.
