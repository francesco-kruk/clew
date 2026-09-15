# Multiplication is composition

Category: **Connections** · Concept ID: `geometry`

A 2 × 2 matrix describes a linear transformation of the plane. Its columns are the images of the basis vectors e₁ = [1, 0]ᵀ and e₂ = [0, 1]ᵀ.

> (AB)x = A(Bx): apply B first, then A

For a rotation example, the matrix [[0, −1], [1, 0]] rotates [2, 1]ᵀ to [−1, 2]ᵀ, a 90° counterclockwise turn. Compare this with stretch, shear, reflection, and projection; their matrices are provided in the structured presets.

To visualize a transformation, compare the unit square with the parallelogram formed by its transformed vertices. Projection flattens it onto a line, losing a coordinate. In AB, B acts first because it is closest to x.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 0  -1 ]
[ 1  0 ]

B =
[ 2 ]
[ 1 ]

AB =
[ -1 ]
[ 2 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `geometry`.
