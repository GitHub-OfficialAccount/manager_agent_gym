"""LS review of S1: independent numeric path for the IRB risk weight.

Second inverse-normal implementation (Acklam's rational approximation + one Halley
refinement step -> ~1e-15 accuracy), written from the published algorithm, NOT from
RE's code. Formula assembled independently from CRE31 text:
    R  = 0.12*(1-e^{-50 PD})/(1-e^{-50}) + 0.24*(1 - (1-e^{-50 PD})/(1-e^{-50}))
    b  = (0.11852 - 0.05478 ln PD)^2
    K  = LGD * ( N( (G(PD) + sqrt(R) G(0.999)) / sqrt(1-R) ) - PD ) * (1+(M-2.5)b)/(1-1.5b)
    RW = K * 12.5 * 100   (percent, no 1.06)
Compares: (a) my path vs RE's NormalDist path per-PD; (b) my path vs published;
(c) residual diagnostics recomputed (sign split, corr(log PD, deviation)).
"""
import math

# --- Acklam inverse normal CDF, plus one Halley refinement ---
A = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
     1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
B = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
     6.680131188771972e+01, -1.328068155288572e+01]
C = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
     -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
D = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
     3.754408661907416e+00]

def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def inv_phi(p):
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        x = (((((C[0]*q+C[1])*q+C[2])*q+C[3])*q+C[4])*q+C[5]) / \
            ((((D[0]*q+D[1])*q+D[2])*q+D[3])*q+1)
    elif p <= phigh:
        q = p - 0.5
        r = q * q
        x = (((((A[0]*r+A[1])*r+A[2])*r+A[3])*r+A[4])*r+A[5])*q / \
            (((((B[0]*r+B[1])*r+B[2])*r+B[3])*r+B[4])*r+1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((C[0]*q+C[1])*q+C[2])*q+C[3])*q+C[4])*q+C[5]) / \
            ((((D[0]*q+D[1])*q+D[2])*q+D[3])*q+1)
    # one Halley step
    e = phi(x) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    x = x - u / (1 + x * u / 2)
    return x

def rw_mine(pd, lgd=0.45, m=2.5):
    decay = (1 - math.exp(-50 * pd)) / (1 - math.exp(-50))
    r = 0.12 * decay + 0.24 * (1 - decay)
    b = (0.11852 - 0.05478 * math.log(pd)) ** 2
    cond = phi((inv_phi(pd) + math.sqrt(r) * inv_phi(0.999)) / math.sqrt(1 - r))
    k = lgd * (cond - pd) * (1 + (m - 2.5) * b) / (1 - 1.5 * b)
    return 12.5 * k * 100.0

PUBLISHED = {
    0.0003: 14.44, 0.0005: 19.65, 0.0010: 29.65, 0.0025: 49.47, 0.0040: 62.72,
    0.0050: 69.61, 0.0075: 82.78, 0.0100: 92.32, 0.0130: 100.95, 0.0150: 105.59,
    0.0200: 114.86, 0.0250: 122.16, 0.0300: 128.44, 0.0400: 139.58, 0.0500: 149.86,
    0.0600: 159.61, 0.1000: 193.09, 0.1500: 221.54, 0.2000: 238.23,
}

from experiments.worker_replacement.test_basel_reference import risk_weight as rw_re

max_impl_gap = 0.0
devs = []
print(f"{'PD':>8}{'published':>10}{'RE-impl':>12}{'LS-indep':>12}{'impl gap':>12}{'dev vs pub':>12}")
for pd in sorted(PUBLISHED):
    a = rw_re(pd, 0.45, 2.5)
    b = rw_mine(pd)
    gap = abs(a - b)
    max_impl_gap = max(max_impl_gap, gap)
    dev = b - PUBLISHED[pd]
    devs.append((math.log(pd), dev))
    print(f"{pd*100:>7.2f}%{PUBLISHED[pd]:>10.2f}{a:>12.6f}{b:>12.6f}{gap:>12.2e}{dev:>+12.4f}")

n = len(devs)
mx = sum(x for x, _ in devs) / n
my = sum(y for _, y in devs) / n
sxy = sum((x - mx) * (y - my) for x, y in devs)
sxx = math.sqrt(sum((x - mx) ** 2 for x, _ in devs))
syy = math.sqrt(sum((y - my) ** 2 for _, y in devs))
corr = sxy / (sxx * syy)
pos = sum(1 for _, y in devs if y > 0)
print(f"\nmax gap between the two independent implementations: {max_impl_gap:.2e} pp")
print(f"sign split vs published: {pos} positive / {n - pos} negative")
print(f"corr(log PD, deviation) = {corr:+.3f}")
print(f"max |deviation| vs published: {max(abs(y) for _, y in devs):.4f} pp")
