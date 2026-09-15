# When a product exists

Category: **The rule** · Concept ID: `shapes`

A row of A must have exactly as many entries as a column of B. That is why A's column count must match B's row count.

> (m × n)(n × p) → m × p

The inner dimensions must agree; the outer dimensions give the output shape. A 2 × 3 matrix times a 3 × 2 matrix produces a 2 × 2 matrix.

Try changing the input shapes. Incompatible inputs have no product: this is not a matrix of zeros and not something we fix by ignoring extra entries.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 1  2  3 ]
[ 4  5  6 ]

B =
[ 1  0 ]
[ 0  1 ]
[ 1  1 ]

AB =
[ 4  5 ]
[ 10  11 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `shapes`.
