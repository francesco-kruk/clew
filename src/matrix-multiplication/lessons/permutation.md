# Permutations rearrange

Category: **Special matrices** · Concept ID: `permutation`

A permutation matrix has exactly one 1 in every row and every column, and zeros elsewhere. It rearranges data rather than blending it.

> PA permutes rows; AP permutes columns

The 3 × 3 left factor in the example swaps rows 1 and 2 while keeping row 3. Every output row copies one input row, because its dot products select just one entry.

For a two-row swap, applying the same swap twice restores the original matrix: P² = I. General permutations need not undo themselves in two steps.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 0  1  0 ]
[ 1  0  0 ]
[ 0  0  1 ]

B =
[ 1  2 ]
[ 3  4 ]
[ 5  6 ]

AB =
[ 3  4 ]
[ 1  2 ]
[ 5  6 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `permutation`.
