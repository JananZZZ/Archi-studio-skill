# Optimization Prompt

After rendering, inspect the actual SVG/layout. Fix in this order:
1. factual/content errors,
2. overlap/out-of-bounds/clipping,
3. unreadable font size,
4. over-dense copy,
5. inconsistent alignment/spacing,
6. weak hierarchy,
7. color imbalance.

Do not solve density primarily by shrinking text. Prefer copy compression, merging, reflow, row/column changes, or height redistribution.
