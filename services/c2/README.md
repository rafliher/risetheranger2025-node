# 🇮🇩 TNI Angkatan Darat - Command & Control System (C2) 🇮🇩

## RAHASIA - TINGKAT KOMANDAN

### Latar Belakang Skenario

Anda adalah seorang **Cybersecurity Specialist** yang ditugaskan untuk melakukan **Red Team Assessment** terhadap sistem Command & Control (C2) milik TNI Angkatan Darat. Sistem ini merupakan infrastruktur kritis yang mengelola komunikasi dan koordinasi operasi militer.

**MISI ANDA:** Identifikasi dan eksploitasi kerentanan sistem untuk menguji ketahanan cybersecurity TNI-AD dan memberikan rekomendasi perbaikan.

---

## 🎯 Objective Challenge

Sistem C2 TNI-AD memiliki multiple layer keamanan dengan berbagai tingkat clearance militer. Untuk menyelesaikan challenge ini, Anda harus:

1. **TAMTAMA Level**: Eksploitasi Format String Vulnerability
2. **BINTARA Level**: Buffer Overflow Exploitation  
3. **PERWIRA Level**: Heap Exploitation Techniques
4. **PERWIRA MENENGAH Level**: Return-to-libc / ROP Chain
5. **PERWIRA TINGGI Level**: Advanced techniques (ret2dlresolve, ASLR bypass)
6. **KOMANDAN Level**: Full system compromise

---

## 🚨 Vulnerability Assessment

### Kerentanan yang Tersedia:

#### 1. **Format String Vulnerabilities**
- Direct `printf()` calls tanpa format specifier
- Stack memory leakage potential
- Arbitrary memory write capabilities
- **Target Functions**: `process_command()`, `system_diagnostics()`

#### 2. **Stack Buffer Overflow** 
- Multiple `strcpy()` tanpa bounds checking
- Stack canary disabled (`-fno-stack-protector`)
- NX bit disabled (`-z execstack`)
- **Target Buffers**: `local_buffer[128]`, `processed_packet[256]`

#### 3. **Heap Vulnerabilities**
- Use After Free (UAF) conditions
- Double Free possibilities  
- Heap buffer overflow
- **Target Functions**: `manage_classified_data()`, `process_command()`

#### 4. **Return-to-libc Attack Vectors**
- `exec_shell()` function available
- `system()` calls accessible
- No PIE (`-no-pie` compilation flag)
- **Target Functions**: `hidden_backdoor()`, `secret_function()`

#### 5. **Advanced Exploitation Techniques**
- ret2dlresolve (when compiled statically)
- Function pointer overwrites
- Integer overflow conditions
- ASLR bypass opportunities

---

## 🛠️ Tools & Environment

### Pre-installed Tools:
```bash
# Debugging & Analysis
gdb, gdb-multiarch, radare2, objdump

# Dynamic Analysis  
strace, ltrace

# Exploitation Framework
pwntools, ropper, checksec

# Binary Analysis
file, readelf, strings

# Network Tools
netcat, socat
```

### Compilation Flags (Maximum Vulnerability):
```bash
-fno-stack-protector    # No stack canaries
-no-pie                 # No PIE 
-fno-pic               # No PIC
-z execstack           # Executable stack
-z norelro             # No RELRO
-Wl,-z,lazy            # Lazy binding
-m32                   # 32-bit (easier exploitation)
```

---

## 🎖️ Progressive Flag System

### Flag Format: `RTR25{TNI_[TECHNIQUE]_[RANK]_[IDENTIFIER]}`

1. **Level 1 - TAMTAMA**: `RTR25{TNI_FORMAT_STRING_BINTARA_ACQUIRED_*}`
2. **Level 2 - BINTARA**: `RTR25{TNI_BUFFER_OVERFLOW_PERWIRA_ACHIEVED_*}`  
3. **Level 3 - PERWIRA**: `RTR25{TNI_HEAP_MASTER_PERWIRA_MENENGAH_CLEARANCE_*}`
4. **Level 4 - PERWIRA MENENGAH**: `RTR25{TNI_ROP_EXPERT_PERWIRA_TINGGI_LEVEL_*}`
5. **Level 5 - PERWIRA TINGGI**: `RTR25{TNI_ADVANCED_TECHNIQUES_KOMANDAN_*}`
6. **Final Flag**: `RTR25{TNI_C2_FULLY_PWNED_KOMANDAN_STATUS_*}`

---

## 🔍 Reconnaissance Tips

### Initial Access:
```bash
# Connect to TNI C2 Binary Service directly
nc target_ip 15000

# SSH for debugging/analysis (optional)
ssh ctfuser@target_ip -p 15022
# Password: TNI_C2_PASSWORD_15000
```

### Exploitation Workflow Examples:

#### Basic Format String Exploitation:
```bash
# Connect to service
nc localhost 15000

# At the TNI-C2> prompt, try format string:
process %p %p %p %p %p %p

# Look for stack leaks and useful addresses
process %6$p

# Try arbitrary write
process %64c%6$hhn
```

#### Buffer Overflow Attack:
```bash
# Send cyclic pattern to find offset
process AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPP

# Once you find the offset, craft exploit
process [padding][ret_address]
```

#### Interactive Exploitation Session:
```bash
# Connect to service  
nc target_ip 15000

# TNI-AD C2 banner appears
# Available commands:
help
process <data>     # Main vulnerability vector
classified         # Heap exploitation 
officer            # Stack overflow in struct
diagnostic         # Format string loop
network            # Function pointer overwrite
```

---

## 💡 Exploitation Hints

### Format String Exploitation:
```python
# Leak stack pointers
payload = "%p %p %p %p %p %p"

# Leak specific addresses
payload = "%6$p"  # Leak 6th parameter

# Arbitrary write
payload = "%64c%6$hhn"  # Write 64 to address at 6th parameter
```

### Buffer Overflow:
```python
# Find offset with cyclic pattern
from pwn import *
pattern = cyclic(200)

# Control EIP
payload = b"A" * offset + p32(target_address)
```

### Heap Exploitation:
```bash
# Trigger UAF sequence
1. classified -> allocate heap chunk
2. [overflow input] -> corrupt heap
3. classified -> use freed chunk
```

### ROP Chain Building:
```python
# Find gadgets
from ropper import *
gadgets = find_gadgets(binary_path)

# Build chain
rop_chain = p32(gadget1) + p32(gadget2) + p32(target_func)
```

---

## 🛡️ Defense Recommendations

Setelah berhasil melakukan exploitation, berikan rekomendasi untuk TNI-AD:

### Immediate Actions:
1. **Enable Stack Protection**: Compile dengan `-fstack-protector-strong`
2. **Enable ASLR**: `echo 2 > /proc/sys/kernel/randomize_va_space`
3. **Enable NX Bit**: Remove `-z execstack` flag
4. **Enable RELRO**: Use full RELRO protection

### Code-level Fixes:
1. **Input Validation**: Implement proper bounds checking
2. **Secure Functions**: Replace `strcpy` dengan `strncpy`
3. **Format String**: Always use format specifiers with printf
4. **Memory Management**: Proper malloc/free handling

### Network Security:
1. **Access Control**: Implement proper authentication
2. **Encryption**: Use TLS/SSL for C2 communications  
3. **Monitoring**: Deploy SIEM for intrusion detection

---

## 📚 References & Learning

### TNI Cybersecurity Context:
- **Bela Negara**: Cybersecurity sebagai bagian pertahanan negara
- **Cyber Warfare**: Ancaman modern terhadap infrastruktur militer
- **Red Team Ops**: Methodology untuk testing defensive capabilities

### Technical References:
- [Format String Attacks](https://owasp.org/www-community/attacks/Format_string_attack)
- [Buffer Overflow Techniques](https://cwe.mitre.org/data/definitions/120.html)
- [Heap Exploitation](https://heap-exploitation.dhavalkapil.com/)
- [Return-to-libc](https://en.wikipedia.org/wiki/Return-to-libc_attack)

---

## ⚠️ Disclaimer

**PERINGATAN PENTING:**
- Challenge ini dibuat untuk tujuan **PENDIDIKAN** dan **CYBERSECURITY TRAINING**
- Teknik yang dipelajari harus digunakan secara **ETIS** dan **LEGAL**
- Untuk meningkatkan kemampuan **DEFENSIVE** cybersecurity TNI-AD
- **DILARANG** menggunakan untuk aktivitas ilegal atau merusak

---

## 🇮🇩 TNI-AD Cyber Defense Unit

*"Kartika Eka Paksi - Siap Melindungi Cyberspace Nusantara"*

**Semper Fidelis - Always Faithful to Nation's Cybersecurity**

---

## 🚀 Getting Started

### Quick Start:
```bash
# 1. Deploy the TNI C2 System
docker-compose up -d

# 2. Connect to the vulnerable binary service
nc localhost 15000

# 3. Alternative: SSH for debugging/analysis
ssh ctfuser@localhost -p 15022
# Password: TNI_C2_PASSWORD_15000
```

### Direct Binary Exploitation:
```bash
# Connect via netcat
nc <target_ip> 15000

# You'll see the TNI C2 banner and prompt
# Start with reconnaissance commands:
help
process test
diagnostic
```

### Local Analysis (via SSH):
```bash
# SSH into the container for analysis
ssh ctfuser@<target_ip> -p 15022

# Analyze the binary
checksec ./niko
objdump -d ./niko | grep -A5 process_command
gdb ./niko

# Run locally for debugging
./niko
```

**Selamat Bertempur, Cyber Warrior TNI! 🎖️**