# Report fixes (keep partner's Imase–Itoh approach for Part 1)

## Part 1 (`part1.tex`)
- [x] Name the construction (Imase–Itoh graph, diameter <= ceil(log_d n)) and drop the false "minus sign just relabels" claim
- [x] Add the missing load-balance point: theta <= 1/ASPL is only reached if link load is even
- [x] Replace "Why this is the best" with an honest near-optimality section (upper bound + measured gap)
- [x] Fix "no topology reaches the bound" (only true when n is a Moore number)
- [x] Fix the n=9 example: actual theta = 0.364 (exact LP), best possible 0.488
- [x] Add `part1.py`: builds the topology, checks degrees, ASPL vs Moore bound, exact theta via Gurobi LP; link it

## Part 2
- [x] `topology.py`: check solver status (T = 0 gives unbounded theta instead of a number)
- [x] Update line-range links after code changes

## Report
- [x] Single PDF (`report.tex` -> `report.pdf`) with repo link, both parts, "we" voice
- [x] Verify: run both scripts, build PDF, check every line link

## Review
- part1.py and topology.py run; part1.py matches independent scipy/networkx checks (same graphs, same theta).
- topology.py results unchanged (0.700 / 0.875 / 0.861 / 0.827); T = 0 now raises instead of returning 1e30.
- LaTeX statically checked (braces, $, environments, cites); every line link checked against the code.
- report.pdf built with tectonic: 5 pages, no LaTeX warnings, all 15 embedded links checked.
