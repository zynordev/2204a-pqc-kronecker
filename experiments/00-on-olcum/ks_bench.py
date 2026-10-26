import random, time, statistics

N, Q = 256, 3329

def schoolbook(a, b):
    c = [0] * N
    for i in range(N):
        ai = a[i]
        for j in range(N):
            k = i + j
            if k < N: c[k] += ai * b[j]
            else: c[k - N] -= ai * b[j]
    return [x % Q for x in c]

# --- Kyber-style NTT (pure Python, reference structure) ---
ZETA = 17
def bitrev7(x): return int(f"{x:07b}"[::-1], 2)
ZETAS = [pow(ZETA, bitrev7(i), Q) for i in range(128)]
GAMMAS = [pow(ZETA, 2 * bitrev7(i) + 1, Q) for i in range(128)]
INV128 = pow(128, -1, Q)

def ntt(f):
    f = f[:]; k = 1; ln = 128
    while ln >= 2:
        for st in range(0, N, 2 * ln):
            z = ZETAS[k]; k += 1
            for j in range(st, st + ln):
                t = z * f[j + ln] % Q
                f[j + ln] = (f[j] - t) % Q
                f[j] = (f[j] + t) % Q
        ln //= 2
    return f

def intt(f):
    f = f[:]; k = 127; ln = 2
    while ln <= 128:
        for st in range(0, N, 2 * ln):
            z = ZETAS[k]; k -= 1
            for j in range(st, st + ln):
                t = f[j]
                f[j] = (t + f[j + ln]) % Q
                f[j + ln] = z * (f[j + ln] - t) % Q
        ln *= 2
    return [x * INV128 % Q for x in f]

def basemul(fa, fb):
    h = [0] * N
    for i in range(128):
        a0, a1, b0, b1 = fa[2*i], fa[2*i+1], fb[2*i], fb[2*i+1]
        h[2*i] = (a0*b0 + a1*b1*GAMMAS[i]) % Q
        h[2*i+1] = (a0*b1 + a1*b0) % Q
    return h

def ntt_mul(a, b):
    return intt(basemul(ntt(a), ntt(b)))

# --- Kronecker substitution ---
def pack(coeffs, l):
    # works for signed coeffs too (Python ints are arbitrary precision)
    x = 0
    for c in reversed(coeffs):
        x = (x << l) + c
    return x

def unpack_signed(x, l, count):
    out = []; mask = (1 << l) - 1; half = 1 << (l - 1)
    for _ in range(count):
        d = x & mask
        if d >= half: d -= 1 << l
        out.append(d)
        x = (x - d) >> l
    return out

def ks_mul(a, b, l, signed):
    A = pack(a, l); B = pack(b, l)
    if signed:
        c = unpack_signed(A * B, l, 2 * N - 1)
    else:
        C = A * B; mask = (1 << l) - 1
        c = [(C >> (l * k)) & mask for k in range(2 * N - 1)]
    return [(c[k] - (c[k + N] if k + N < 2 * N - 1 else 0)) % Q for k in range(N)]

# Negacyclic directly: integers mod 2^(N*l)+1 (X^256+1 evaluated at 2^l)
def ks_negacyclic(a, b, l):
    M = (1 << (N * l)) + 1
    C = (pack(a, l) * pack(b, l)) % M
    if C > M // 2: C -= M
    return [x % Q for x in unpack_signed(C, l, N)]

def centered(x): return x - Q if x > Q // 2 else x

def rand_poly(): return [random.randrange(Q) for _ in range(N)]
def rand_small(eta): return [random.randint(-eta, eta) for _ in range(N)]

def bench(f, reps):
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter_ns(); f(); ts.append(time.perf_counter_ns() - t0)
    return statistics.median(ts) / 1000

if __name__ == "__main__":
    random.seed(1)
    # correctness
    for _ in range(200):
        a = rand_poly(); s = rand_small(3); sm = [x % Q for x in s]
        ref = schoolbook(a, sm)
        assert ntt_mul(a, sm) == ref
        assert ks_mul(a, sm, 32, False) == ref
        assert ks_mul([centered(x) for x in a], s, 22, True) == ref
        assert ks_negacyclic([centered(x) for x in a], s, 22) == ref
    print("correctness OK")

    a = rand_poly(); s = rand_small(3); sm = [x % Q for x in s]; ac = [centered(x) for x in a]
    print(f"schoolbook        {bench(lambda: schoolbook(a, sm), 30):9.1f} us")
    print(f"NTT (pure Python) {bench(lambda: ntt_mul(a, sm), 300):9.1f} us")
    print(f"KS unsigned 32b   {bench(lambda: ks_mul(a, sm, 32, False), 2000):9.1f} us")
    print(f"KS signed 22b     {bench(lambda: ks_mul(ac, s, 22, True), 2000):9.1f} us")
    print(f"KS negacyc 22b    {bench(lambda: ks_negacyclic(ac, s, 22), 2000):9.1f} us")
    A32, B32 = pack(a, 32), pack(sm, 32); A22, B22 = pack(ac, 22), pack(s, 22)
    print(f"  only bigint mul 8192b: {bench(lambda: A32 * B32, 20000):.2f} us, 5632b: {bench(lambda: A22 * B22, 20000):.2f} us")

    # how big do coefficients actually get? (random vs adversarial)
    mx = 0
    for _ in range(2000):
        a = [centered(x) for x in rand_poly()]; s = rand_small(3)
        c = [0] * (2 * N - 1)
        for i in range(N):
            for j in range(N): c[i + j] += a[i] * s[j]
        mx = max(mx, max(abs(x) for x in c))
    print(f"random-case max |c| over 2000 trials: {mx} (~{mx.bit_length()} bits); worst case 1277952 (21 bits)")
    for l in (21, 20, 19, 18, 17):
        bad = 0
        for _ in range(300):
            a = [centered(x) for x in rand_poly()]; s = rand_small(3)
            if ks_mul(a, s, l, True) != schoolbook(a, [x % Q for x in s]): bad += 1
        print(f"  l={l}: {bad}/300 wrong (random inputs)")
    # adversarial: attacker picks a = 1664*sign pattern aligned with s
    s = rand_small(3); a = [0] * N
    k = N - 1
    for i in range(N):
        j = k - i
        a[i] = 1664 * (1 if s[j] >= 0 else -1)
    for l in (21, 20, 19, 18):
        print(f"  adversarial l={l}: {'OK' if ks_mul(a, s, l, True) == schoolbook(a, [x % Q for x in s]) else 'WRONG'}")
