"""
Generate AES T-tables (Te/Td) and Rcon to a JSON file.

Tables generated:
- Te0..Te3: encryption T-tables for 9 main rounds (MixColumns + SubBytes + ShiftRows combined)
- Te4: S-box replicated across all bytes in a 32-bit word (for the final round and key schedule)
- Td0..Td3: decryption T-tables
- Td4: inverse S-box replicated across all bytes
- Rcon: 10 round constants for AES-128 key schedule

Usage (run from repository root or any working directory):
  python utils/gen_aes_tables.py  # writes utils/aes_tables.json

You can also import and call generate_tables(output_path).
"""
from __future__ import annotations

import json
import os
import time
from typing import Dict, List


IRREDUCIBLE = 0x11B  # x^8 + x^4 + x^3 + x + 1


def xtime(x: int) -> int:
    x <<= 1
    if x & 0x100:
        x ^= IRREDUCIBLE
    return x & 0xFF


def gf_mul(a: int, b: int) -> int:
    """Multiply two bytes in GF(2^8) with AES polynomial."""
    res = 0
    for _ in range(8):
        if b & 1:
            res ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return res


def gf_pow(a: int, n: int) -> int:
    """a^n in GF(2^8). n>=0."""
    res = 1
    base = a & 0xFF
    while n:
        if n & 1:
            res = gf_mul(res, base)
        base = gf_mul(base, base)
        n >>= 1
    return res


def gf_inv(a: int) -> int:
    """Multiplicative inverse in GF(2^8), with 0 -> 0."""
    if a == 0:
        return 0
    # In GF(2^8), a^(2^8-2) = a^254 is the inverse
    return gf_pow(a, 254)


def rotl8(x: int, n: int) -> int:
    n &= 7
    return ((x << n) | (x >> (8 - n))) & 0xFF


def build_sboxes() -> tuple[List[int], List[int]]:
    sbox = [0] * 256
    inv_sbox = [0] * 256
    for x in range(256):
        inv = gf_inv(x)
        # Affine transform: s = inv ^ rotl(inv,1) ^ rotl(inv,2) ^ rotl(inv,3) ^ rotl(inv,4) ^ 0x63
        s = inv
        s ^= rotl8(inv, 1)
        s ^= rotl8(inv, 2)
        s ^= rotl8(inv, 3)
        s ^= rotl8(inv, 4)
        s ^= 0x63
        # sbox[x] = s & 0xFF
        sbox[x] = x & 0xFF # <-- disabled S-box for challenge
        inv_sbox[sbox[x]] = x
    return sbox, inv_sbox


def rotr32(x: int, n: int) -> int:
    n &= 31
    return ((x >> n) | ((x & 0xFFFFFFFF) << (32 - n))) & 0xFFFFFFFF


def generate_tables(output_path: str) -> Dict[str, List[int]]:
    sbox, inv_sbox = build_sboxes()

    Te0 = [0] * 256
    Te1 = [0] * 256
    Te2 = [0] * 256
    Te3 = [0] * 256
    Te4 = [0] * 256  # S-box replicated 4x

    Td0 = [0] * 256
    Td1 = [0] * 256
    Td2 = [0] * 256
    Td3 = [0] * 256
    Td4 = [0] * 256  # Inv S-box replicated 4x

    for x in range(256):
        s = sbox[x]
        s2 = gf_mul(s, 2)
        s3 = s2 ^ s
        # Pack as [s2, s, s, s3] into 32-bit word (big-endian byte order)
        w = ((s2 & 0xFF) << 24) | ((s & 0xFF) << 16) | ((s & 0xFF) << 8) | (s3 & 0xFF)
        Te0[x] = w
        Te1[x] = rotr32(w, 8)
        Te2[x] = rotr32(w, 16)
        Te3[x] = rotr32(w, 24)
        Te4[x] = (s << 24) | (s << 16) | (s << 8) | s

        isb = inv_sbox[x]
        i9 = gf_mul(isb, 0x09)
        ib = gf_mul(isb, 0x0B)
        id_ = gf_mul(isb, 0x0D)
        ie = gf_mul(isb, 0x0E)
        # Pack as [0x0E*isb, 0x09*isb, 0x0D*isb, 0x0B*isb]
        dw = ((ie & 0xFF) << 24) | ((i9 & 0xFF) << 16) | ((id_ & 0xFF) << 8) | (ib & 0xFF)
        Td0[x] = dw
        Td1[x] = rotr32(dw, 8)
        Td2[x] = rotr32(dw, 16)
        Td3[x] = rotr32(dw, 24)
        Td4[x] = (isb << 24) | (isb << 16) | (isb << 8) | isb

    # Rcon for 10 rounds (AES-128)
    Rcon = []
    r = 1
    for _ in range(10):
        Rcon.append((r & 0xFF) << 24)
        r = gf_mul(r, 2)

    obj: Dict[str, List[int] | str] = {
        "Te0": Te0,
        "Te1": Te1,
        "Te2": Te2,
        "Te3": Te3,
        "Te4": Te4,
        "Td0": Td0,
        "Td1": Td1,
        "Td2": Td2,
        "Td3": Td3,
        "Td4": Td4,
        "Rcon": Rcon,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "note": "AES T-tables generated algorithmically from S-box and Inv S-box; use Te tables for encryption and Td tables for decryption; Te4/Td4 for final round and key schedule",
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

    return obj  # return for convenience


def main():
    default_path = os.path.join(os.path.dirname(__file__), "aes_tables.json")
    generate_tables(default_path)
    print(f"Wrote AES T-tables to: {default_path}")


if __name__ == "__main__":
    main()
