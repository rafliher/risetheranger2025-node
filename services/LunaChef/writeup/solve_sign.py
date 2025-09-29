import hashlib
import random
import secrets
import math
from typing import List, Tuple

q = 12 * 1024 + 1
n = 64

def trim(p: List[int]) -> List[int]:
    while len(p) > 1 and p[-1] % q == 0:
        p.pop()
    return p

def poly_mod_q(p: List[int]) -> List[int]:
    return [x % q for x in p]

def poly_zero() -> List[int]:
    return [0]

def poly_add(a: List[int], b: List[int]) -> List[int]:
    L = max(len(a), len(b))
    res = [( (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) ) % q for i in range(L)]
    return trim(res)

def poly_sub(a: List[int], b: List[int]) -> List[int]:
    L = max(len(a), len(b))
    res = [( (a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) ) % q for i in range(L)]
    return trim(res)

def mul_plain(a: List[int], b: List[int]) -> List[int]:
    if (not a) or (not b):
        return [0]
    res = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        ai = a[i] % q
        if ai == 0:
            continue
        for j in range(len(b)):
            res[i+j] = (res[i+j] + ai * (b[j] % q)) % q
    return trim(res)

def negacyclic_reduce_coeffs(poly_long: List[int], n_local: int) -> List[int]:
    res = [0] * n_local
    for idx, coeff in enumerate(poly_long):
        c = coeff % q
        if idx < n_local:
            res[idx] = (res[idx] + c) % q
        else:
            pos = idx - n_local
            res[pos] = (res[pos] - c) % q
    return [x % q for x in res]

def negacyclic_mul(a: List[int], b: List[int]) -> List[int]:
    long = mul_plain(a, b)
    return negacyclic_reduce_coeffs(long, n)

def modinv_int(a: int, m: int) -> int:
    a = a % m
    if a == 0:
        raise ZeroDivisionError("no inverse for 0")
    t0, t1 = 0, 1
    r0, r1 = m, a
    while r1 != 0:
        qk = r0 // r1
        r0, r1 = r1, r0 - qk * r1
        t0, t1 = t1, t0 - qk * t1
    if r0 != 1:
        raise ValueError("no inverse")
    return t0 % m

def poly_divmod(a: List[int], b: List[int]) -> Tuple[List[int], List[int]]:
    a = [x % q for x in a.copy()]
    b = [x % q for x in b.copy()]
    a = trim(a); b = trim(b)
    if len(b) == 0 or (len(b) == 1 and b[0] % q == 0):
        raise ZeroDivisionError("poly div by zero")
    deg_a = len(a) - 1
    deg_b = len(b) - 1
    if deg_a < deg_b:
        return [0], a
    lc_b = b[-1] % q
    inv_lc_b = modinv_int(lc_b, q)
    quotient = [0] * (deg_a - deg_b + 1)
    rem = a.copy()
    while len(rem) - 1 >= deg_b and not (len(rem) == 1 and rem[0] == 0):
        deg_r = len(rem) - 1
        coeff = (rem[-1] * inv_lc_b) % q
        pos = deg_r - deg_b
        quotient[pos] = coeff
        for i in range(len(b)):
            rem[pos + i] = (rem[pos + i] - coeff * b[i]) % q
        rem = trim(rem)
    return trim(quotient), trim(rem)

def poly_gcd_ext(a: List[int], b: List[int]) -> Tuple[List[int], List[int], List[int]]:
    a = [x % q for x in a.copy()]; b = [x % q for x in b.copy()]
    a = trim(a); b = trim(b)
    r0, r1 = a, b
    s0, s1 = [1], [0]
    t0, t1 = [0], [1]
    while not (len(r1) == 1 and r1[0] == 0):
        q_poly, r2 = poly_divmod(r0, r1)
        s2 = poly_sub(s0, mul_plain(q_poly, s1))
        t2 = poly_sub(t0, mul_plain(q_poly, t1))
        r0, r1 = r1, r2
        s0, s1 = s1, s2
        t0, t1 = t1, t2
    return trim(r0), trim(s0), trim(t0)

def poly_inv_mod_xn1(f_poly: List[int]) -> List[int]:
    m = [0] * (n + 1)
    m[0] = 1
    m[-1] = 1
    g, s, t = poly_gcd_ext(f_poly.copy(), m.copy())
    g = [x % q for x in g]
    if len(g) != 1:
        raise ValueError("gcd degree > 0, no inverse modulo x^n+1")
    c = g[0] % q
    inv_c = modinv_int(c, q)
    inv = [ (coeff * inv_c) % q for coeff in s ]
    return negacyclic_reduce_coeffs(inv, n)

def hash_to_poly(msg: bytes) -> List[int]:
    out = []
    ctr = 0
    h = hashlib.sha256()
    h.update(msg)
    while len(out) < n:
        digest = hashlib.sha256(h.digest() + ctr.to_bytes(4, "little")).digest()
        for i in range(0, len(digest), 2):
            if len(out) >= n:
                break
            val = int.from_bytes(digest[i:i+2], "little") % q
            out.append(val)
        ctr += 1
    return out[:n]

def sample_small_poly(bound: int) -> List[int]:
    if bound <= 0:
        return [0 for _ in range(n)]

    if bound >= 5:
        sigma = bound / 5.0
    else:
        sigma = max(1.5, bound / 2.0)

    def _u01() -> float:
        r = secrets.randbits(53)
        return (r + 1) / (2**53 + 1)

    def _gauss0() -> float:
        u1 = _u01()
        u2 = _u01()
        return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

    out: List[int] = []
    while len(out) < n:
        z = _gauss0()
        x = int(round(z * sigma))
        if -bound <= x <= bound:
            out.append(x)
    return out

def poly_to_hex(p):
    """Convert polynomial/vector to single hex string"""
    return ''.join(f"{x % q:04x}" for x in p)

def hex_to_poly(hs):
    """Convert single hex string back to polynomial/vector"""
    return [int(hs[i:i+4], 16) for i in range(0, len(hs), 4)]


import time
import requests

host = "localhost"
port = 14000
protokol = "http"

session = requests.Session()

def sign(test_data):
    endpoint_sign = f'{protokol}://{host}:{port}/sign'
    r = session.post(endpoint_sign, data={'data': test_data}, timeout=5, verify=False)
    assert r.status_code == 200, f'Signing request failed, status {r.status_code}'
    resp_json = r.json()
    endpoint_signature = resp_json.get('signature', '')
    return endpoint_signature[len(endpoint_signature)//2:]

m1 = "test"
m2 = "test2"
m3 = "test3"
m4 = "test4"
rspon1 = sign(m1)
rspon2 = sign(m2)
rspon3 = sign(m3)
rspon4 = sign(m4)

def op(message, signature):
    message = message.encode()
    s1, s2 = signature[:len(signature)//2], signature[len(signature)//2:]
    s1 = hex_to_poly(s1)
    s2 = hex_to_poly(s2)
    m = hash_to_poly(message)
    return m, s1, s2

m1, s11, s21 = op(m1, rspon1)
m2, s12, s22 = op(m2, rspon2)
m3, s13, s23 = op(m3, rspon3)
m4, s14, s24 = op(m4, rspon4)

# recover h from s1, s2, m
# nonce3 s1 + h s2 + nonce4 = m1
# nonce3 s1 + h s2 + nonce4 = m2
def recover_h(list_s1, list_s2, list_m):
    m1, m2, m3, m4 = list_m
    s11, s12, s13, s14 = list_s1
    s21, s22, s23, s24 = list_s2
    m12 = poly_sub(m1, m2)
    m34 = poly_sub(m3, m4)
    s11s12 = poly_sub(s11, s12)
    s13s14 = poly_sub(s13, s14)
    s21s22 = poly_sub(s21, s22)
    s23s24 = poly_sub(s23, s24)
    m1, m2 = m12, m34
    a1, a2 = s11s12, s13s14
    b1, b2 = s21s22, s23s24
    b1a = negacyclic_mul(a2, b1)
    b2a = negacyclic_mul(a1, b2)
    m1a = negacyclic_mul(a2, m1)
    m2a = negacyclic_mul(a1, m2)
    a = poly_sub(b1a, b2a)
    m = poly_sub(m1a, m2a)
    h = negacyclic_mul(poly_inv_mod_xn1(a), m)
    return h

# print(poly_inv_mod_xn1(s11))
s1 = [s11, s12, s13, s14]
s2 = [s21, s22, s23, s24]
m = [m1, m2, m3, m4]
h = recover_h(s1, s2, m)
print(h)
# h = [11473, 884, 4368, 536, 36, 1500, 8653, 2459, 10893, 9588, 8615, 3354, 9216, 5249, 7290, 4900, 589, 8530, 1804, 4922, 2733, 6834, 4426, 5823, 6944, 6452, 4003, 485, 11687, 6757, 7955, 11188, 3905, 12091, 8180, 8313, 7295, 6725, 10707, 4360, 4926, 958, 8586, 5366, 2994, 4652, 5167, 3906, 8557, 11251, 6786, 4444, 11396, 3515, 10332, 10993, 9494, 5504, 9819, 11252, 5086, 5187, 4127, 4556]
print(len(h))

from sage.all import *
q = 12 * 1024 + 1
n = 64

P = PolynomialRing(Zmod(q), names='x')
x = P.gens()[0]
R = P.quotient(x ** n + 1)

M = Matrix(ZZ, 2 * n, 2 * n)

M[:n, :n] = identity_matrix(ZZ, n)
M[n:, n:] = q * identity_matrix(ZZ, n)

h = R(h)

M[:n, n:] = Matrix(ZZ, [(h * R([0] * i + [1])).list() for i in range(n)])

L = M.BKZ(block_size=n // 2)
row = L[0]

center = lambda x: int(Mod(x, q).lift_centered())

f, g = R(list(row[:n])), R(list(row[n:]))
assert h == g * f.inverse()

f_list = list(map(center, f.list()))
g_list = list(map(center, g.list()))

print(f_list)
print(g_list)

# do some reduce function