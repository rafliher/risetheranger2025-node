# signing_service.py

from config import signing_key

class SigningService:
    def __init__(self, run_keygen=False):
        # ambil langsung dari config
        self.N = signing_key["N"]
        self.q = signing_key["q"]
        self.h = signing_key["h"]

        self.p = 3
        self.f = None
        self.g = None
        self.f_qinv = None
        self.f_pinv = None

        # hanya jika ingin generate key baru
        if run_keygen:
            self.keygen()

    # ---------------------------------------------------
    # polynomial helpers (saya cut ke yang dibutuhkan saja)
    # ---------------------------------------------------
    def _poly_mul(self, a, b, mod):
        res = [0] * self.N
        for i in range(self.N):
            ai = a[i] if i < len(a) else 0
            if ai == 0: 
                continue
            for j in range(self.N):
                bj = b[j] if j < len(b) else 0
                if bj == 0: 
                    continue
                k = (i + j) % self.N
                res[k] = (res[k] + ai * bj) % mod
        return res

    def _poly_scalar_mul(self, a, scalar, mod):
        return [(ai * scalar) % mod for ai in a]

    def _message_to_poly(self, message):
        if isinstance(message, str):
            bs = [ord(c) & 0xff for c in message]
        elif isinstance(message, bytes):
            bs = list(message)
        else:
            bs = [int(message) & 0xff]
        poly = [0] * self.N
        for i, b in enumerate(bs):
            poly[i % self.N] = (poly[i % self.N] + (b % self.p)) % self.p
        return poly

    def _poly_to_hex(self, poly):
        return "".join(f"{(coeff % self.q):04x}" for coeff in poly)

    def _hex_to_poly(self, hex_str):
        poly = []
        for i in range(0, len(hex_str), 4):
            poly.append(int(hex_str[i:i+4], 16) % self.q)
        if len(poly) < self.N:
            poly.extend([0] * (self.N - len(poly)))
        elif len(poly) > self.N:
            poly = poly[:self.N]
        return poly

    # ---------------------------------------------------
    # Sign & Verify
    # ---------------------------------------------------
    def sign(self, message):
        if self.h is None:
            raise ValueError("public key not loaded")
        mpoly = self._message_to_poly(message)
        s = self._poly_mul(mpoly, self.h, self.q)  # contoh sederhana
        return {"signature": self._poly_to_hex(s)}

    def verify(self, signature_hex, message):
        s = self._hex_to_poly(signature_hex)
        mpoly = self._message_to_poly(message)
        v = self._poly_mul(self.h, s, self.q)
        recovered = [c % self.p for c in v]
        return recovered == mpoly

# ---------------------------------------------------
# Example usage
# ---------------------------------------------------
if __name__ == "__main__":
    svc = SigningService()
    msg = "hello"
    sig = svc.sign(msg)
    print("[+] Signature:", sig["signature"][:60], "...")
    valid = svc.verify(sig["signature"], msg)
    print("[+] Verify:", valid)
