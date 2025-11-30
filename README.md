# simplex.py
solve linear programming simplex problems with a python script because you got
nothing better to do in your life. or maybe you do so you don't want to waste
your time solving LP problems.


```
[nima@pluto ~]$ cat simplex.txt
min z = -x1 - 2x2
4x1 + 5x2 <= 20
-x1 + x2 <= 3
[nima@pluto ~]$ simplex.py simplex.txt
┌──────┬──────┬──────┬──────┬───────┐
│   x1 │   x2 │   s1 │   s2 │   RHS │
├──────┼──────┼──────┼──────┼───────┤
│    1 │    2 │    0 │    0 │     0 │
│    4 │    5 │    1 │    0 │    20 │
│   -1 │    1 │    0 │    1 │     3 │
└──────┴──────┴──────┴──────┴───────┘
Selected col 1 (x2) to be entered
Selected row 2 to be exited
Used basic row operation R0 = R0 - 2R2
Used basic row operation R1 = R1 - 5R2
┌──────┬──────┬──────┬──────┬───────┐
│   x1 │   x2 │   s1 │   s2 │   RHS │
├──────┼──────┼──────┼──────┼───────┤
│    3 │    0 │    0 │   -2 │    -6 │
│    9 │    0 │    1 │   -5 │     5 │
│   -1 │    1 │    0 │    1 │     3 │
└──────┴──────┴──────┴──────┴───────┘
Selected col 0 (x1) to be entered
Selected row 1 to be exited
Used basic row operation R1 = R1/9
Used basic row operation R0 = R0 - 3R1
Used basic row operation R2 = R2 + 1R1
┌──────┬──────┬──────┬──────┬───────┐
│   x1 │   x2 │ s1   │ s2   │ RHS   │
├──────┼──────┼──────┼──────┼───────┤
│    0 │    0 │ -1/3 │ -1/3 │ -23/3 │
│    1 │    0 │ 1/9  │ -5/9 │ 5/9   │
│    0 │    1 │ 1/9  │ 4/9  │ 32/9  │
└──────┴──────┴──────┴──────┴───────┘
[nima@pluto ~]$
```
