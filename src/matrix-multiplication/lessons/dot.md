# A row meets a column

Category: **The rule** · Concept ID: `dot`

Multiply matching entries, then add the products. This row-by-column calculation is a dot product: it is the single operation behind every entry of a matrix product.

> [a₁  a₂  a₃] [b₁  b₂  b₃]ᵀ = [a₁b₁ + a₂b₂ + a₃b₃]

Here the row [2, 3, −1] meets the column [4, 1, 2]ᵀ. The result is [2·4 + 3·1 + (−1)·2] = [9]. The superscript T turns a row into a column.

Build the sum one pair at a time. The output is a 1 × 1 matrix, not a row of three separate products.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 2  3  -1 ]

B =
[ 4 ]
[ 1 ]
[ 2 ]

AB =
[ 9 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `dot`.
