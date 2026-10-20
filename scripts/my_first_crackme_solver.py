from z3 import *

MASK_32  = 0xFFFFFFFF
MASK_64  = 0xFFFFFFFFFFFFFFFF
MASK_128 = (1 << 128) - 1

MASK_1 = 0x000000FF000000FF000000FF000000FF
MASK_2 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00

TARGET_LOW_64 = 0x56252CAB5D734876
KEY_CONSTANT = 0x1337


def z3_srli_epi16(x, shift):
    out = BitVecVal(0, 128)
    for i in range(8):
        shifted = LShR(Extract(16 * i + 15, 16 * i, x), shift)
        out = out | (ZeroExt(112, shifted) << (16 * i))
    return out

def z3_srli_epi32(x, shift):
    out = BitVecVal(0, 128)
    for i in range(4):
        shifted = LShR(Extract(32 * i + 31, 32 * i, x), shift)
        out = out | (ZeroExt(96, shifted) << (32 * i))
    return out

def z3_packus_epi16(a, b):
    out = BitVecVal(0, 128)
    for i in range(8):
        lane = Extract(16 * i + 15, 16 * i, a)
        out = out | (If(ULE(lane, BitVecVal(0xFF, 16)),
                        ZeroExt(112, lane),
                        BitVecVal(0xFF, 128)) << (8 * i))
    for i in range(8):
        lane = Extract(16 * i + 15, 16 * i, b)
        out = out | (If(ULE(lane, BitVecVal(0xFF, 16)),
                        ZeroExt(112, lane),
                        BitVecVal(0xFF, 128)) << (8 * (8 + i)))
    return out

def z3_unpacklo_8bit(a, b):
    out = BitVecVal(0, 128)
    for i in range(8):
        out = out | (ZeroExt(120, Extract(8 * i + 7, 8 * i, a)) << (16 * i))
        out = out | (ZeroExt(120, Extract(8 * i + 7, 8 * i, b)) << (16 * i + 8))
    return out

def z3_shuffle_32bit(x, control):
    lanes = [Extract(32 * i + 31, 32 * i, x) for i in range(4)]
    out = BitVecVal(0, 128)
    for i in range(4):
        out = out | (ZeroExt(96, lanes[(control >> (2 * i)) & 3]) << (32 * i))
    return out

def z3_shuffle_lo16(x, control):
    low = [Extract(16 * i + 15, 16 * i, x) for i in range(4)]
    out = x & BitVecVal(MASK_128 ^ MASK_64, 128)
    for i in range(4):
        out = out | (ZeroExt(112, low[(control >> (2 * i)) & 3]) << (16 * i))
    return out

def z3_shuffle_hi16(x, control):
    high = [Extract(16 * (4 + i) + 15, 16 * (4 + i), x) for i in range(4)]
    out = x & BitVecVal(MASK_64, 128)
    for i in range(4):
        out = out | (ZeroExt(112, high[(control >> (2 * i)) & 3]) << (16 * (4 + i)))
    return out

def derive_constant_vector():
    w32 = lambda e: e & MASK_32
    k = KEY_CONSTANT

    q0 = w32(-1029531031 * k -  740551042)
    q1 = w32(-1923058979 * k - 1776570451)
    q2 = w32( -807543007 * k -  853684456)
    q3 = w32(  268046093 * k - 1353011855)
    v = z3_srli_epi32(BitVecVal(q0 | (q1 << 32) | (q2 << 64) | (q3 << 96), 128), 0x10) & BitVecVal(MASK_1, 128)

    r0 = w32(-283353463 * k +  551188310)
    r1 = w32( 1524104789 * k - 1343933481)
    r2 = w32( -936169423 * k + 1772930244)
    r3 = w32( 1811824153 * k +  958313186)
    w = z3_srli_epi32(BitVecVal(r0 | (r1 << 32) | (r2 << 64) | (r3 << 96), 128), 0x10) & BitVecVal(MASK_1, 128)

    return z3_packus_epi16(v, w)

CONSTANT_VECTOR_Z3 = derive_constant_vector()


def compute_low64_z3(b):
    user_input = ZeroExt(64, Concat(b[7], b[6], b[5], b[4], b[3], b[2], b[1], b[0]))
    loaded     = ZeroExt(64, Concat(b[13], b[12], b[11], b[10], b[9], b[8], b[7], b[6]))
    interleaved = z3_unpacklo_8bit(loaded, BitVecVal(0, 128))

    a = z3_shuffle_hi16(interleaved, 220)
    a = z3_shuffle_32bit(a, 156)
    a = z3_shuffle_lo16(a, 72)

    bb = z3_shuffle_32bit(interleaved, 39)
    bb = z3_shuffle_lo16(bb, 200)
    bb = z3_shuffle_32bit(bb, 108)
    bb = z3_shuffle_lo16(bb, 112)
    bb = z3_shuffle_hi16(bb, 147)

    packed_a = z3_packus_epi16(a, a)
    packed_b = z3_packus_epi16(bb, bb)
    packed_c = z3_packus_epi16(CONSTANT_VECTOR_Z3, CONSTANT_VECTOR_Z3)

    mask2     = BitVecVal(MASK_2, 128)
    not_mask2 = BitVecVal(MASK_128 ^ MASK_2, 128)

    term1 = (not_mask2 & user_input) | (packed_b & mask2)
    term2 = (packed_a & mask2) | (not_mask2 & z3_srli_epi16(user_input, 8))
    return Extract(63, 0, term1 ^ term2 ^ packed_c)


def magic_const(mul, add):
    return ((mul * KEY_CONSTANT + add) & MASK_32) >> 16 & 0xFF

K_B0    = magic_const( 1103515245,       12345)
K_X1    = magic_const(-2139243339, -1492899873)
K_X2X3  = magic_const( -301564143,  -698016724)
K_X3X4  = magic_const( -341751747,   229283573)
K_X4X5  = magic_const( -740534279, -1038148470)
K_X6    = magic_const(-1691004155,  1051550459)


# ---------- sanity check ----------
KNOWN_FLAG = b"Xor_N0t_3nough"
known_bytes = [BitVecVal(c, 8) for c in KNOWN_FLAG]
result = simplify(compute_low64_z3(known_bytes))
print(f"[*] known flag low64: {result}")
print(f"[*] target low64:     {hex(TARGET_LOW_64)}")

probe = Solver()
probe.add(result != BitVecVal(TARGET_LOW_64, 64))
if probe.check() == sat:
    print("[-] PIPELINE MISMATCH")
    exit(1)
print("[+] pipeline verified against known flag")


# ---------- full solve: SIMD + scalar ----------
print("[*] solving with SIMD + scalar constraints...")
b = [BitVec(f'b{i}', 8) for i in range(14)]
s = Solver()

# SIMD constraint
s.add(compute_low64_z3(b) == BitVecVal(TARGET_LOW_64, 64))

# Scalar constraints — the six `&&` clauses
s.add(b[0]                                 == BitVecVal(0x35 ^ K_B0, 8))
s.add(b[2] ^ b[1] ^ BitVecVal(K_X1, 8)     == BitVecVal(0x14, 8))
s.add(BitVecVal(K_X2X3, 8) ^ b[2] ^ b[3]   == BitVecVal(0x15, 8))
s.add(BitVecVal(K_X3X4, 8) ^ b[3] ^ b[4]   == BitVecVal(0xBC, 8))
s.add(BitVecVal(K_X4X5, 8) ^ b[4] ^ b[5]   == BitVecVal(0x83, 8))
s.add(b[5] ^ b[6] ^ BitVecVal(K_X6, 8)     == BitVecVal(0x0F, 8))

# length / printable
for byte in b:
    s.add(byte >= 0x20, byte <= 0x7e)

if s.check() == sat:
    m = s.model()
    sol = bytes([m[b[i]].as_long() for i in range(14)])
    print(f"[+] solved: {sol}")
    print(f"[+] flag:   CMO{{{sol.decode()}}}")
else:
    print("[-] no solution — scalar or SIMD constraint is wrong")