import itertools
import random

import gurobipy as gp
from gurobipy import GRB

N = 8
D = 4


def best_topology(T, n=N, d=D):
    """Find the topology (and routing) that maximizes concurrent flow for traffic matrix T."""
    m = gp.Model("best_topology")
    m.Params.OutputFlag = 0

    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]

    # x[u,v] = number of links from u to v (parallel links allowed)
    x = m.addVars(pairs, vtype=GRB.INTEGER, lb=0, ub=d, name="x")
    # f[s,u,v] = flow from source s that goes over link u->v
    f = m.addVars(range(n), pairs, lb=0, name="f")
    # theta = fraction of every demand that is delivered
    theta = m.addVar(lb=0, name="theta")

    m.setObjective(theta, GRB.MAXIMIZE)

    # every node has d outgoing and d incoming links
    for u in range(n):
        m.addConstr(gp.quicksum(x[u, v] for v in range(n) if v != u) == d)
        m.addConstr(gp.quicksum(x[v, u] for v in range(n) if v != u) == d)

    # flow conservation: source s sends theta * T[s][t] to every t
    for s in range(n):
        for w in range(n):
            out_flow = gp.quicksum(f[s, w, v] for v in range(n) if v != w)
            in_flow = gp.quicksum(f[s, v, w] for v in range(n) if v != w)
            if w == s:
                m.addConstr(out_flow - in_flow == theta * sum(T[s]))
            else:
                m.addConstr(in_flow - out_flow == theta * T[s][w])

    # capacity: total flow on u->v is at most the number of links (each capacity 1)
    for u, v in pairs:
        m.addConstr(gp.quicksum(f[s, u, v] for s in range(n)) <= x[u, v])

    m.optimize()
    if m.Status != GRB.OPTIMAL:  # e.g. T = 0 makes theta unbounded
        raise RuntimeError(f"no optimal topology (Gurobi status {m.Status})")

    links = {(u, v): round(x[u, v].X) for u, v in pairs if x[u, v].X > 0.5}
    return theta.X, links


def random_hose_tm(n=N, d=D, k=5, seed=None):
    """Random hose traffic matrix: a random mix of k permutations with no self-traffic, scaled by d."""
    rng = random.Random(seed)
    derangements = [p for p in itertools.permutations(range(n)) if all(p[i] != i for i in range(n))]
    weights = [rng.random() for _ in range(k)]
    total = sum(weights)
    T = [[0.0] * n for _ in range(n)]
    for w in weights:
        p = rng.choice(derangements)
        for i in range(n):
            T[i][p[i]] += d * w / total
    return T


def uniform_tm(n=N, d=D):
    return [[0 if i == j else d / (n - 1) for j in range(n)] for i in range(n)]


if __name__ == "__main__":
    tests = [("uniform", uniform_tm())]
    tests += [(f"random hose #{i}", random_hose_tm(seed=i)) for i in range(3)]

    for name, T in tests:
        theta, links = best_topology(T)
        print(f"{name}: theta = {theta:.3f}")
        for (u, v), c in sorted(links.items()):
            print(f"  {u} -> {v}: {c} link(s)")
