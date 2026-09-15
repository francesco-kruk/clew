# Regroup, but do not reorder

Category: **Connections** · Concept ID: `laws`

Matrix multiplication is associative and distributes over addition when the dimensions fit. Associativity changes parentheses, not the order of the factors.

> (AB)C = A(BC)   ·   A(B + C) = AB + AC

Consider A = [1, 2] (1 × 2), B = [[1, 0], [0, 1]] (2 × 2), and C = [3, 4]ᵀ (2 × 1). Group left: AB = [1, 2], so (AB)C = [11]. Group right: BC = [3, 4]ᵀ, so A(BC) = [11].

Grouping can radically change computation cost. For shapes (10 × 100), (100 × 5), (5 × 50), forming (AB)C uses 7,500 scalar multiplications; A(BC) uses 75,000. The answers agree in exact arithmetic, though floating-point rounding may differ.

The worked example shows the final dot product from both groupings above. For an (m × n)(n × p) product, the direct algorithm uses mnp scalar multiplications.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 1  2 ]

B =
[ 3 ]
[ 4 ]

AB =
[ 11 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `laws`.
