# A column meets a row

Category: **Connections** · Concept ID: `outer`

A column times a row gives an outer product, not a dot product. It expands two vectors into a matrix. This is a useful bridge to rank, factorizations, and large-scale computation.

> (m × 1)(1 × n) → m × n   ·   AB = Σₖ A[:, k] B[k, :]

Here [1, 2, −1]ᵀ[3, 4] = [[3, 4], [6, 8], [−3, −4]]. Every row is a multiple of the same row vector, so this nonzero matrix has rank 1.

Any matrix product is a sum of outer products: pair each column of A with the matching row of B, then add. For [[1, 2], [3, 4]][[5, 6], [7, 8]], the two outer products are [[5, 6], [15, 18]] and [[14, 16], [28, 32]]. Their sum is [[19, 22], [43, 50]].

You now have three views of the same operation: row–column dot products, weighted sums of columns, and sums of outer products. Rank, least squares, eigenvectors, and singular-value decomposition build on these foundations.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 1 ]
[ 2 ]
[ -1 ]

B =
[ 3  4 ]

AB =
[ 3  4 ]
[ 6  8 ]
[ -3  -4 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `outer`.
