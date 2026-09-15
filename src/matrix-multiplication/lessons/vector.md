# A matrix acts on a vector

Category: **Building the product** · Concept ID: `vector`

A column vector is a matrix with one column. Multiplying A by a vector computes one dot product for every row of A.

> Ax = x₁·(column 1 of A) + x₂·(column 2 of A)

With x = [2, 1]ᵀ, the first output is 1·2 + 2·1 = 4, and the second is 3·2 + 1·1 = 7. Thus Ax = [4, 7]ᵀ.

There is another way to see the same result: take twice A's first column [1, 3]ᵀ, then add its second column [2, 1]ᵀ. Matrix multiplication forms weighted sums of columns.

For a coordinate view, plot x and Ax as arrows from the origin. Changing A changes the transformation; changing x changes the input.

## Worked example

The factors are written as rows. Every result entry is a row-column dot product.

```text
A =
[ 1  2 ]
[ 3  1 ]

B =
[ 2 ]
[ 1 ]

AB =
[ 4 ]
[ 7 ]
```

The machine-readable example, additional presets, and checkpoint are in [map.json](../map.json), under node `vector`.
