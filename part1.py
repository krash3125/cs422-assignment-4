from collections import Counter, deque

import gurobipy as gp
from gurobipy import GRB


def build_topology(n, d):
    """Part 1 topology: Imase-Itoh links i -> (-d*i - j) mod n, then swap out self-loops."""
    links = Counter((i, (-d * i - j) % n) for i in range(n) for j in range(1, d + 1))
    # replace a->a and u->v with u->a and a->v (degrees stay d)
    for a in [u for u, v in links if u == v]:
        u, v = next((u, v) for u, v in links
                    if u != v and a not in (u, v) and not links[u, a] and not links[a, v])
        links.subtract([(a, a), (u, v)])
        links.update([(u, a), (a, v)])
        links = +links
    return links


def path_length_sum(links, n):
    """Sum of shortest-path hop counts over all ordered pairs (BFS from every node)."""
    out = [[] for _ in range(n)]
    for u, v in links:
        out[u].append(v)
    total = 0
    for s in range(n):
        dist = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for v in out[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        total += sum(dist.values())
    return total


def moore_sum(n, d):
    """Smallest possible sum of hop counts from one node: d nodes at 1 hop, d^2 at 2 hops, ..."""
    left, h, total = n - 1, 1, 0
    while left > 0:
        k = min(d ** h, left)
        total += k * h
        left -= k
        h += 1
    return total


def concurrent_flow(links, n, d):
    """Exact max concurrent flow theta on a fixed topology for the uniform traffic matrix."""
    m = gp.Model("concurrent_flow")
    m.Params.OutputFlag = 0

    demand = d / (n - 1)
    f = m.addVars(range(n), list(links), lb=0, name="f")
    theta = m.addVar(lb=0, name="theta")
    m.setObjective(theta, GRB.MAXIMIZE)

    for s in range(n):
        for w in range(n):
            out_flow = gp.quicksum(f[s, w, v] for (u, v) in links if u == w)
            in_flow = gp.quicksum(f[s, u, w] for (u, v) in links if v == w)
            m.addConstr(out_flow - in_flow == (theta * d if w == s else -theta * demand))
    for e, c in links.items():
        m.addConstr(gp.quicksum(f[s, e[0], e[1]] for s in range(n)) <= c)

    m.optimize()
    return theta.X


if __name__ == "__main__":
    # every node has d links in and out, no self-loops; path lengths vs the Moore bound
    worst = (0.0, (0, 0))
    for n in range(4, 120):
        for d in range(2, n - 1):
            if (n - 1) % d:
                continue
            links = build_topology(n, d)
            assert all(u != v for u, v in links)
            for i in range(n):
                assert sum(c for (u, _), c in links.items() if u == i) == d
                assert sum(c for (_, v), c in links.items() if v == i) == d
            gap = path_length_sum(links, n) / (n * moore_sum(n, d)) - 1
            worst = max(worst, (gap, (n, d)))
    print(f"all n < 120 with d | n-1: valid topology; avg path length at most "
          f"{worst[0]:.1%} above the Moore bound (worst case n, d = {worst[1]})")

    print("\n n  d  avg path  theta (exact)  upper bound  ratio")
    for n, d in [(9, 2), (13, 3), (16, 3), (17, 4), (21, 4), (25, 3)]:
        links = build_topology(n, d)
        theta = concurrent_flow(links, n, d)
        bound = (n - 1) / moore_sum(n, d)
        aspl = path_length_sum(links, n) / (n * (n - 1))
        print(f"{n:2d} {d:2d}  {aspl:8.3f}  {theta:13.3f}  {bound:11.3f}  {theta / bound:5.1%}")
