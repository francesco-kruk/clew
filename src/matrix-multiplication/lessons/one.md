# One number at a time

Category: **The rule** · Concept ID: `one`

A matrix is a rectangular array of numbers. Its shape is written rows × columns. A 1 × 1 matrix has just one entry, so multiplying two of them is ordinary multiplication in brackets.

> [a] [b] = [ab]

In the example, [3][4] = [12]. The brackets tell us to regard 3 and 4 as matrices; the arithmetic has not changed.

Try replacing either input with another number. The selected row of A and column of B each contain just one entry.

A scalar is a number, not a 1 × 1 matrix. Scalar multiplication 3B scales every entry of B; the matrix product [3]B follows the shape rule you will meet shortly.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 3 ]

B =
[ 4 ]

AB =
[ 12 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `one`.
