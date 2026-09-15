# Every output is a dot product

Category: **Building the product** · Concept ID: `rectangle`

For AB, entry (i, j) is row i of A dotted with column j of B. Repeat this rule for each output position. Here we number rows and columns starting at 1.

> (AB)ᵢⱼ = Σₖ Aᵢₖ Bₖⱼ

For the 2 × 3 and 3 × 2 inputs below, entry (1, 2) is 1·2 + 2·1 + 3·0 = 4. Entry (2, 1) is 0·1 + (−1)·0 + 2·3 = 6.

Choose any output entry and trace its row and column. For the larger 3 × 2 by 2 × 4 example, the same small rule produces twelve entries. Equivalently, multiply A by each column of B in turn.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 1  2  3 ]
[ 0  -1  2 ]

B =
[ 1  2 ]
[ 0  1 ]
[ 3  0 ]

AB =
[ 10  4 ]
[ 6  -1 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `rectangle`.
