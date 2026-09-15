# Undoing a transformation

Category: **Connections** · Concept ID: `inverse`

An inverse undoes a square matrix: A⁻¹A = AA⁻¹ = I. Not every square matrix has one. A transformation that collapses distinct inputs cannot be undone uniquely.

> A = [[a, b], [c, d]]: invertible exactly when ad − bc ≠ 0

The shear [[1, 1], [0, 1]] is undone by [[1, −1], [0, 1]]. Their product is I₂. For a 2 × 2 matrix, the inverse is 1/(ad − bc) times [[d, −b], [−c, a]].

A projection such as [[1, 0], [0, 0]] has determinant zero and no inverse: it erases the second coordinate. If A and B are invertible, (AB)⁻¹ = B⁻¹A⁻¹: undo the last operation first.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 1  1 ]
[ 0  1 ]

B =
[ 1  -1 ]
[ 0  1 ]

AB =
[ 1  0 ]
[ 0  1 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `inverse`.
