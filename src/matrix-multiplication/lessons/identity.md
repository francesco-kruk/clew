# Identity and zero

Category: **Special matrices** · Concept ID: `identity`

The identity matrix has ones on its main diagonal and zeros elsewhere. It preserves every vector and matrix of compatible size. A zero matrix has only zero entries.

> IₘA = A = AIₙ   ·   A0 = 0   ·   0A = 0

For A of shape m × n, the left identity is m × m and the right identity is n × n. They need not be the same size.

In the example, I₂ leaves a 2 × 3 matrix unchanged. Replace I₂ with a 2 × 2 zero matrix: every dot product becomes a sum of zeros. The zero output still has the outer dimensions of the factors.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 1  0 ]
[ 0  1 ]

B =
[ 2  -1  4 ]
[ 3  5  0 ]

AB =
[ 2  -1  4 ]
[ 3  5  0 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `identity`.
