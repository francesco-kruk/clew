# Transposing reverses the order

Category: **Connections** · Concept ID: `transpose`

The transpose exchanges rows and columns. It turns an m × n matrix into an n × m matrix. A product's transpose reverses the factors as well as transposing them.

> (AB)ᵀ = BᵀAᵀ

Here A is 2 × 3 and B is 3 × 1, so AB is 2 × 1. Its transpose is 1 × 2. On the other side, Bᵀ is 1 × 3 and Aᵀ is 3 × 2: the dimensions match.

Transpose the numerical product and compare it with BᵀAᵀ. The order reverses because rows become columns and columns become rows.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 1  2  0 ]
[ 0  -1  3 ]

B =
[ 2 ]
[ 1 ]
[ 4 ]

AB =
[ 4 ]
[ 11 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `transpose`.
