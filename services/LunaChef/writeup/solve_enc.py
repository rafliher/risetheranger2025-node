import time
import requests

import os
import sys
from typing import List

# Make project's src importable to get AES implementation
CUR_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CUR_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)


def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, 'big')


def int_to_bytes(x: int, n: int = 16) -> bytes:
    return x.to_bytes(n, 'big')


class GF2Matrix:
    """A small, efficient GF(2) matrix using Python integers for row bitsets.

    - rows: list[int], each int has ncols bits (bit j is column j)
    - operations: + (XOR), *, transpose, pow, inverse
    """

    __slots__ = ('nrows', 'ncols', 'rows')

    def __init__(self, nrows: int, ncols: int, rows: List[int] | None = None):
        self.nrows = nrows
        self.ncols = ncols
        if rows is None:
            self.rows = [0] * nrows
        else:
            assert len(rows) == nrows
            self.rows = list(rows)

    @staticmethod
    def zeros(nrows: int, ncols: int) -> 'GF2Matrix':
        return GF2Matrix(nrows, ncols)

    @staticmethod
    def identity(n: int) -> 'GF2Matrix':
        rows = [(1 << i) for i in range(n)]
        return GF2Matrix(n, n, rows)

    def copy(self) -> 'GF2Matrix':
        return GF2Matrix(self.nrows, self.ncols, self.rows[:])

    def set(self, i: int, j: int, v: int) -> None:
        if v & 1:
            self.rows[i] |= (1 << j)
        else:
            self.rows[i] &= ~(1 << j)

    def get(self, i: int, j: int) -> int:
        return (self.rows[i] >> j) & 1


    def __add__(self, other: 'GF2Matrix') -> 'GF2Matrix':
        assert self.nrows == other.nrows and self.ncols == other.ncols
        return GF2Matrix(self.nrows, self.ncols, [r ^ o for r, o in zip(self.rows, other.rows)])

    def __sub__(self, other: 'GF2Matrix') -> 'GF2Matrix':
        # same as addition in GF(2)
        return self.__add__(other)

    def transpose(self) -> 'GF2Matrix':
        n, m = self.nrows, self.ncols
        t_rows = [0] * m
        for j in range(m):
            col_bits = 0
            mask = 1 << j
            for i in range(n):
                bit = 1 if (self.rows[i] & mask) else 0
                col_bits |= (bit << i)
            t_rows[j] = col_bits
        return GF2Matrix(m, n, t_rows)

    @staticmethod
    def from_blocks(blocks: List[List['GF2Matrix']]) -> 'GF2Matrix':
        # blocks is 2D list; all blocks in a row must have same nrows; all in a column same ncols
        total_rows = sum(blocks[i][0].nrows for i in range(len(blocks)))
        total_cols = sum(blocks[0][j].ncols for j in range(len(blocks[0])))
        out_rows: List[int] = []
        for brow in blocks:
            row_height = brow[0].nrows
            # sanity
            for b in brow:
                assert b.nrows == row_height
            for r in range(row_height):
                combined = 0
                offset = 0
                for b in brow:
                    combined |= (b.rows[r] << offset)
                    offset += b.ncols
                out_rows.append(combined)
        return GF2Matrix(total_rows, total_cols, out_rows)

    def mul(self, other: 'GF2Matrix') -> 'GF2Matrix':
        assert self.ncols == other.nrows
        n, k, m = self.nrows, self.ncols, other.ncols
        # Precompute columns of other as k-bit integers
        bcols = [0] * m
        for j in range(m):
            col = 0
            for i in range(k):
                bit = (other.rows[i] >> j) & 1
                col |= (bit << i)
            bcols[j] = col
        res_rows = [0] * n
        for i in range(n):
            arow = self.rows[i]
            row_res = 0
            for j in range(m):
                # parity of popcount(arow & bcols[j])
                if (arow & bcols[j]).bit_count() & 1:
                    row_res |= (1 << j)
            res_rows[i] = row_res
        return GF2Matrix(n, m, res_rows)

    def __matmul__(self, other: 'GF2Matrix') -> 'GF2Matrix':
        return self.mul(other)

    def __mul__(self, other: 'GF2Matrix') -> 'GF2Matrix':
        return self.mul(other)

    def __pow__(self, e: int) -> 'GF2Matrix':
        assert self.nrows == self.ncols
        result = GF2Matrix.identity(self.nrows)
        base = self.copy()
        exp = e
        while exp > 0:
            if exp & 1:
                result = result.mul(base)
            base = base.mul(base)
            exp >>= 1
        return result

    def inverse(self) -> 'GF2Matrix':
        assert self.nrows == self.ncols
        n = self.nrows
        # augmented matrix rows as 2n-bit integers: [self | I]
        aug = [self.rows[i] | (1 << (n + i)) for i in range(n)]
        mask_n = (1 << n) - 1

        row = 0
        for col in range(n):
            # find pivot
            pivot = None
            for r in range(row, n):
                if (aug[r] >> col) & 1:
                    pivot = r
                    break
            if pivot is None:
                raise ValueError('Matrix not invertible over GF(2)')
            # swap to current row
            if pivot != row:
                aug[row], aug[pivot] = aug[pivot], aug[row]
            # eliminate other rows
            for r in range(n):
                if r != row and ((aug[r] >> col) & 1):
                    aug[r] ^= aug[row]
            row += 1
            if row == n:
                break

        inv_rows = [ (aug[i] >> n) & mask_n for i in range(n) ]
        return GF2Matrix(n, n, inv_rows)


def bytes2mat(b: bytes) -> GF2Matrix:
    # 1 x 128 row with bit j equals MSB-first bit stream of bytes
    assert len(b) == 16
    bits_row = 0
    idx = 0
    for by in b:
        for k in range(7, -1, -1):
            bit = (by >> k) & 1
            if bit:
                bits_row |= (1 << idx)
            idx += 1
    return GF2Matrix(1, 128, [bits_row])


def mat2bytes(m: GF2Matrix) -> bytes:
    assert m.nrows == 1 and m.ncols == 128
    row = m.rows[0]
    out = bytearray(16)
    for i in range(16):
        val = 0
        base = i * 8
        for k in range(8):
            bit = (row >> (base + k)) & 1
            val |= (bit << (7 - k))  # MSB-first in each byte
        out[i] = val
    return bytes(out)


def build_linear_layers() -> GF2Matrix:
    # Build 8x8 identity and X
    I8 = GF2Matrix.identity(8)
    X = GF2Matrix.zeros(8, 8)
    for i in range(7):
        X.set(i, i + 1, 1)
    for r0 in (3, 4, 6, 7):
        X.set(r0, 0, 1)

    # 32x32 C matrix as 4x4 blocks of 8x8
    C = GF2Matrix.from_blocks([
        [X,          X + I8,     I8,        I8],
        [I8,         X,          X + I8,    I8],
        [I8,         I8,         X,         X + I8],
        [X + I8,     I8,         I8,        X],
    ])

    Z8 = GF2Matrix.zeros(8, 8)
    Z32 = GF2Matrix.zeros(32, 32)

    o0 = GF2Matrix.from_blocks([
        [I8, Z8, Z8, Z8],
        [Z8, Z8, Z8, Z8],
        [Z8, Z8, Z8, Z8],
        [Z8, Z8, Z8, Z8],
    ])
    o1 = GF2Matrix.from_blocks([
        [Z8, Z8, Z8, Z8],
        [Z8, I8, Z8, Z8],
        [Z8, Z8, Z8, Z8],
        [Z8, Z8, Z8, Z8],
    ])
    o2 = GF2Matrix.from_blocks([
        [Z8, Z8, Z8, Z8],
        [Z8, Z8, Z8, Z8],
        [Z8, Z8, I8, Z8],
        [Z8, Z8, Z8, Z8],
    ])
    o3 = GF2Matrix.from_blocks([
        [Z8, Z8, Z8, Z8],
        [Z8, Z8, Z8, Z8],
        [Z8, Z8, Z8, Z8],
        [Z8, Z8, Z8, I8],
    ])

    S = GF2Matrix.from_blocks([
        [o0, o1, o2, o3],
        [o3, o0, o1, o2],
        [o2, o3, o0, o1],
        [o1, o2, o3, o0],
    ])

    M = GF2Matrix.from_blocks([
        [C,   Z32, Z32, Z32],
        [Z32, C,   Z32, Z32],
        [Z32, Z32, C,   Z32],
        [Z32, Z32, Z32, C  ],
    ])

    R = M * S
    A = S * (R ** 9)  # matches original comment
    return A

host = "52.221.242.191"
port = 14000
protokol = "http"

session = requests.Session()

endpoint_encrypt = f'{protokol}://{host}:{port}/encrypt'
endpoint_decrypt = f'{protokol}://{host}:{port}/decrypt'
endpoint_script = f'{protokol}://{host}:{port}/scripts/encryption'
test_text = f"TestText-{int(time.time())}"
r = session.post(endpoint_encrypt, data={'text': test_text}, timeout=5, verify=False)
assert r.status_code == 200, f'Encryption request failed, status {r.status_code}'
resp_json = r.json()
enc = resp_json.get('encrypted_data', '')
block_enc = enc[:-64]

A = build_linear_layers()
ct = bytes.fromhex(block_enc)
ct_list = [ct[i:i+16] for i in range(0, len(ct), 16)]

def getPlain(p_known, ct_known, ct_want):
    p2_vec = bytes2mat(p_known).transpose()
    ct2_vec = bytes2mat(ct_known).transpose()
    K = ct2_vec + (A * p2_vec)
    ct_vec = bytes2mat(ct_want).transpose()
    recovered_bits = (A.inverse() * (ct_vec + K)).transpose()
    recovered = mat2bytes(recovered_bits)
    return recovered

for pad_len in range(1, 17):
    pad = bytes([pad_len] * pad_len)
    p_known = (test_text.encode() + pad)[-16:]

    recovered = getPlain(p_known, ct_list[-1], ct_list[0])
    if(b'RTRTNI25' in recovered):
        flag = recovered
        for i in ct_list[1:-1]:
            flag += getPlain(p_known, ct_list[-1], i)
        
        print(flag)