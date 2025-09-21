# junk.py
# Toy "full" Falcon-like implementation with real polynomial inverse mod (x^n+1, q)
# NOT CRYPTOGRAPHICALLY SECURE. Educational/demo only.
import hashlib
import random
from typing import List, Tuple

# Parameters
q = 12 * 1024 + 1   # 12289
n = 64

# -----------------------
# Basic poly helpers (coeff vectors length variable; index 0 is const term)
# -----------------------
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
    # reduce modulo x^n + 1: x^n ≡ -1
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
    # naive convolution then reduce by x^n + 1
    long = mul_plain(a, b)
    return negacyclic_reduce_coeffs(long, n)

# -----------------------
# Integer modular inverse
# -----------------------
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

# -----------------------
# Polynomial division a // b over Z_q (plain polynomials, not mod x^n+1)
# Returns (quotient, remainder)
# -----------------------
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
        # rem = rem - coeff * x^pos * b
        for i in range(len(b)):
            rem[pos + i] = (rem[pos + i] - coeff * b[i]) % q
        rem = trim(rem)
    return trim(quotient), trim(rem)

# -----------------------
# Extended Euclidean for polynomials over Z_q
# returns (g, s, t) with s*a + t*b = g
# -----------------------
def poly_gcd_ext(a: List[int], b: List[int]) -> Tuple[List[int], List[int], List[int]]:
    a = [x % q for x in a.copy()]; b = [x % q for x in b.copy()]
    a = trim(a); b = trim(b)
    # initialize
    r0, r1 = a, b
    s0, s1 = [1], [0]
    t0, t1 = [0], [1]
    while not (len(r1) == 1 and r1[0] == 0):
        q_poly, r2 = poly_divmod(r0, r1)
        # s2 = s0 - q_poly * s1
        s2 = poly_sub(s0, mul_plain(q_poly, s1))
        t2 = poly_sub(t0, mul_plain(q_poly, t1))
        r0, r1 = r1, r2
        s0, s1 = s1, s2
        t0, t1 = t1, t2
    return trim(r0), trim(s0), trim(t0)

# -----------------------
# Inverse of f modulo (x^n + 1, q)
# If gcd(f, x^n+1) = c (constant), then inverse exists as s * c^{-1}
# -----------------------
def poly_inv_mod_xn1(f_poly: List[int]) -> List[int]:
    # modulus m(x) = x^n + 1
    m = [0] * (n + 1)
    m[0] = 1
    m[-1] = 1
    g, s, t = poly_gcd_ext(f_poly.copy(), m.copy())
    g = [x % q for x in g]
    if len(g) != 1:
        raise ValueError("gcd degree > 0, no inverse modulo x^n+1")
    c = g[0] % q
    inv_c = modinv_int(c, q)
    # s * inv_c is the inverse (mod m)
    inv = [ (coeff * inv_c) % q for coeff in s ]
    # reduce inv modulo x^n + 1 (negacyclic reduction)
    return negacyclic_reduce_coeffs(inv, n)

# -----------------------
# Hash -> polynomial
# -----------------------
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
    return [random.randint(-bound, bound) for _ in range(n)]

def poly_to_hex(p):
    """Convert polynomial/vector to single hex string"""
    return ''.join(f"{x % q:04x}" for x in p)

def hex_to_poly(hs):
    """Convert single hex string back to polynomial/vector"""
    return [int(hs[i:i+4], 16) for i in range(0, len(hs), 4)]


# -----------------------
# Keygen / Sign / Verify
# -----------------------
class SigningService:
    def __init__(self, small_bound: int = 4):
        self.small_bound = small_bound
        self.f = None
        self.g = None
        self.F = None
        self.G = None
        self.h = None
        self._keygen_until_invertible()

    def _keygen_until_invertible(self):
        tries = 0
        while True:
            tries += 1
            # f should be invertible modulo (x^n+1,q). Choose random small-ish f with odd constant
            f_candidate = [random.randint(1, q-1) for _ in range(n)]
            # make f coefficients small-ish? it's okay to be random
            try:
                inv_f = poly_inv_mod_xn1(f_candidate)
            except Exception:
                continue
            # g small
            g_candidate = sample_small_poly(self.small_bound)
            # compute h = g * f^{-1} mod (x^n+1, q)
            h_candidate = negacyclic_mul(g_candidate, inv_f)
            # accept
            self.f = [x % q for x in f_candidate]
            self.g = [x % q for x in g_candidate]
            self.F = sample_small_poly(self.small_bound)
            self.G = sample_small_poly(self.small_bound)
            self.h = [x % q for x in h_candidate]
            # done
            break

    def sign(self, message: bytes) -> Tuple[List[int], List[int]]:
        # m polynomial
        message = message.encode()
        m = hash_to_poly(message)
        # sample small s2 (in real Falcon: sample via trapdoor Gaussian)
        s2 = sample_small_poly(self.small_bound)
        # s1 = m - s2 * h  (mod x^n+1, q)
        s2h = negacyclic_mul(s2, self.h)
        s1 = poly_sub(m, s2h)
        s1 = [x % q for x in s1]
        s2 = [x % q for x in s2]
        sResult = poly_to_hex(s1) + poly_to_hex(s2)
        result = {
            "success": True,
            "signature": sResult,
        }
        return result

    def verify(self, signature, message) -> bool:
        message = message.encode()
        s1, s2 = signature[:len(signature)//2], signature[len(signature)//2:]
        s1 = hex_to_poly(s1)
        s2 = hex_to_poly(s2)
        m = hash_to_poly(message)
        s2h = negacyclic_mul(s2, self.h)
        lhs = poly_add(s1, s2h)
        lhs = [x % q for x in lhs]
        m = [x % q for x in m]
        result = {
            "success": True,
            "valid": lhs == m,
        }
        return result
    
signing_service = SigningService()