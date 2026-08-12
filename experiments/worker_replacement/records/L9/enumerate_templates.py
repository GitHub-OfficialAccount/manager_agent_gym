"""Independent enumeration of admissible lattice templates — RR.

Built from the PREDICATE AS DOCUMENTED, not from LS's or RE's code, and validated
first on a population whose answer is already published (the 210 five-class
lattices, 57.1% admissible) before being pointed at anything unknown.
"""
from itertools import combinations, permutations


def props(P, S, w2, w3):
    """All structural facts about an ordered template, computed once."""
    post = (S, w2, w3)                      # roster post-swap
    pre = (P, S, w2, w3)
    def coverers_post(x):
        return sum(1 for w in post if x in w)
    def coverers_pre(x):
        return sum(1 for w in pre if x in w)
    lie = P - S                             # classes the stale card wrongly claims for S
    return {
        # 1. predecessor and successor share something but not everything
        "partial_overlap": 0 < len(P & S) < len(P),
        "disjoint": len(P & S) == 0,
        # 2. a lied-about class nobody covers post-swap -> interior spread
        "sole_held": any(coverers_post(x) == 0 for x in lie),
        # 3. a DIFFERENT lied-about class with exactly one coverer -> the lie
        #    costs coverage rather than mere displacement
        "singly_covered_lie": any(
            coverers_post(x) == 0 and any(
                coverers_post(y) == 1 for y in lie if y != x)
            for x in lie),
        # 4. successor strictly required post-swap
        "succ_required_post": any(
            x in S and coverers_post(x) == 1 for x in S),
        # the generator's own pre-swap version of the same idea: a class with
        # exactly two holders, which is what _designate_swap_pair looks for
        "class_with_two_holders": any(
            coverers_pre(x) == 2 for x in set().union(*pre)),
        "sole_held_pre": any(coverers_pre(x) == 1 for x in set().union(*pre)),
        # 5. no class left uncovered pre-swap
        "all_classes_covered": len(set().union(*pre)),
    }


def enumerate_ordered(n_classes, size, predicate):
    classes = range(n_classes)
    subsets = [frozenset(c) for c in combinations(classes, size)]
    hits = []
    for tup in permutations(subsets, 4):
        if predicate(props(*tup), n_classes):
            hits.append(tup)
    return hits


def fmt(t, n_classes):
    letters = "abcdefgh"
    return " ".join("".join(letters[i] for i in sorted(s)) for s in t)


# ---------------------------------------------------------------------------
# POSITIVE CONTROL 1 — the published 210 / 57.1% five-class free-draw figure.
# _lattice_from_template's docstring: "free draws at five classes satisfy them
# only 57.1% of the time (210 lattices enumerated by LS)". The properties named
# there are: distinct + equal size (automatic), a class with exactly two holders,
# and a class held by exactly one worker.
print("=" * 78)
print("POSITIVE CONTROL 1 — the published 210 lattices / 57.1% at five classes")
print("=" * 78)
subsets5 = [frozenset(c) for c in combinations(range(5), 2)]
unordered = list(combinations(subsets5, 4))
print(f"unordered 4-subsets of C(5,2)=10 sets : {len(unordered)}   (published: 210)")
ok = 0
for combo in unordered:
    pre = combo
    universe = set().union(*pre)
    def cov(x):
        return sum(1 for w in pre if x in w)
    two = any(cov(x) == 2 for x in universe)
    one = any(cov(x) == 1 for x in universe)
    if two and one:
        ok += 1
print(f"satisfying (a class with 2 holders) AND (a class with 1 holder): "
      f"{ok}/{len(unordered)} = {ok / len(unordered):.1%}   (published: 57.1%)")

# ---------------------------------------------------------------------------
# POSITIVE CONTROL 2 — the three NAMED templates must land where the team's own
# documents say they land.
print()
print("=" * 78)
print("POSITIVE CONTROL 2 — the three named templates, classified by my predicate")
print("=" * 78)
named = {
    "current":           ("ae", "ab", "bc", "cd"),
    "proposed_disjoint": ("de", "ab", "ce", "cb"),
    "partial_overlap":   ("ae", "ab", "ce", "cb"),
}
idx = {ch: i for i, ch in enumerate("abcdef")}
for name, spec in named.items():
    tup = tuple(frozenset(idx[ch] for ch in s) for s in spec)
    p = props(*tup)
    print(f"{name:<20} partial_overlap={str(p['partial_overlap']):<5} "
          f"sole_held={str(p['sole_held']):<5} "
          f"singly_covered_lie={str(p['singly_covered_lie']):<5} "
          f"succ_required_post={str(p['succ_required_post']):<5}")

# ---------------------------------------------------------------------------
# The claim under attack, at coverage size 2 — must be 0 for any class count.
print()
print("=" * 78)
print("THE SIZE-2 IMPOSSIBILITY CLAIM (published: 0 at 5, 6 and 7 classes)")
print("=" * 78)


def core(p, n):
    return p["partial_overlap"] and p["sole_held"] and p["singly_covered_lie"]


for n in (5, 6, 7):
    hits = enumerate_ordered(n, 2, core)
    print(f"  size 2, {n} classes : {len(hits):>7} ordered templates")

# ---------------------------------------------------------------------------
# THE 6,480 / 12,960 CLAIM, under every reading of "admissible" I can construct.
print()
print("=" * 78)
print("THE CLAIM UNDER ATTACK — size 3, six classes (published: 12,960 ordered,")
print("6,480 up to incumbent symmetry)")
print("=" * 78)

variants = {
    "core three conditions only":
        core,
    "+ successor strictly required post-swap":
        lambda p, n: core(p, n) and p["succ_required_post"],
    "+ every class covered pre-swap":
        lambda p, n: core(p, n) and p["all_classes_covered"] == n,
    "+ both of the above":
        lambda p, n: (core(p, n) and p["succ_required_post"]
                      and p["all_classes_covered"] == n),
    "+ a class with exactly two holders (the generator's derived rule)":
        lambda p, n: core(p, n) and p["class_with_two_holders"],
}
for label, pred in variants.items():
    hits = enumerate_ordered(6, 3, pred)
    n = len(hits)
    print(f"  {label:<62} {n:>7} ordered  {n // 2:>7} /2  "
          f"{'<== MATCHES' if n in (12960, 6480) or n // 2 in (12960, 6480) else ''}")

# universe size, for reference
subs = list(combinations(range(6), 3))
print(f"\n  universe: C(6,3)={len(subs)} subsets, "
      f"{len(subs) * (len(subs) - 1) * (len(subs) - 2) * (len(subs) - 3)} ordered 4-tuples")
