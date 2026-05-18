with open('enctry', 'r', encoding='utf-8') as f:
    enc = f.read()

flag = ""

for c in enc:
    val = ord(c)
    high_byte = (val >> 8) & 0xFF
    low_byte = val & 0xFF

flag += chr(high_byte) + chr(low_byte)

print(repr(flag))
