# Diagonal matrices scale

Category: **Special matrices** · Concept ID: `diagonal`

A diagonal matrix has zeros away from the main diagonal. Multiplication by it scales rows or columns, depending on which side it is on.

> DA scales rows of A; AD scales columns of A

Here D = diag(2, −1) is the left factor. DB doubles the first row of B and negates the second row.

Reverse the order. BD instead doubles B's first column and negates its second. A scalar multiple cI is a special diagonal matrix: it scales all rows or columns by the same c.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 2  0 ]
[ 0  -1 ]

B =
[ 1  3 ]
[ 2  4 ]

AB =
[ 2  6 ]
[ -2  -4 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `diagonal`.
