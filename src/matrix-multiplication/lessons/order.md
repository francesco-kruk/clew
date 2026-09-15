# Order matters

Category: **Building the product** · Concept ID: `order`

In general, AB and BA are different. Sometimes only one is defined. Even when both exist and have the same shape, their entries need not agree.

> AB ≠ BA in general

For these square matrices, AB = [[2, 1], [1, 1]], while BA = [[1, 1], [1, 2]]. Reversing the order changes which rows meet which columns.

Compute BA to compare it with AB. Matrix multiplication is also not entrywise multiplication: entrywise multiplication of equally shaped matrices simply multiplies corresponding entries without summing.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 1  1 ]
[ 0  1 ]

B =
[ 1  0 ]
[ 1  1 ]

AB =
[ 2  1 ]
[ 1  1 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `order`.
