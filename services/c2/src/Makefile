# TNI-AD C2 System Compilation
# Intentionally vulnerable compilation for CTF

CC = gcc
TARGET = tni_c2_system
SOURCE = tni_c2_system.c

# Vulnerability-enabling compilation flags
VULN_FLAGS = -fno-stack-protector    # Disable stack canaries
VULN_FLAGS += -no-pie                # Disable PIE for easier ROP
VULN_FLAGS += -fno-pic               # Disable PIC
VULN_FLAGS += -z execstack           # Enable executable stack
VULN_FLAGS += -z norelro             # Disable RELRO
VULN_FLAGS += -Wl,-z,lazy            # Enable lazy binding for ret2dlresolve

# Debug flags for easier exploitation
DEBUG_FLAGS = -g                     # Include debug symbols
DEBUG_FLAGS += -O0                   # No optimization

# Additional flags for maximum vulnerability
# EXPLOIT_FLAGS = -m32                 # 32-bit for easier exploitation (comment out for 64-bit)
# EXPLOIT_FLAGS += -static           # Static linking (uncomment for ret2dlresolve)

# Warning suppression (don't warn about dangerous functions)
SUPPRESS = -w

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CC) $(VULN_FLAGS) $(DEBUG_FLAGS) $(EXPLOIT_FLAGS) $(SUPPRESS) -o $(TARGET) $(SOURCE) -ldl

# 64-bit version with different vulnerabilities
64bit:
	$(CC) $(VULN_FLAGS) $(DEBUG_FLAGS) $(SUPPRESS) -o $(TARGET) $(SOURCE) -ldl

# Static version for ret2dlresolve
static:
	$(CC) $(VULN_FLAGS) $(DEBUG_FLAGS) -static $(SUPPRESS) -o $(TARGET) $(SOURCE)

# Maximum vulnerability version
max_vuln:
	$(CC) -fno-stack-protector -no-pie -fno-pic -z execstack -z norelro -Wl,-z,lazy -g -O0 -w -o $(TARGET) $(SOURCE) -ldl

clean:
	rm -f $(TARGET)

# Generate clearance token for the challenge
token:
	echo "$(shell date +%s)" > clearance_token

# Show security features of compiled binary
check:
	file $(TARGET)
	objdump -h $(TARGET) | grep -E "(RELRO|STACK|NX|PIE|CANARY)"
	readelf -l $(TARGET) | grep -E "(GNU_STACK|GNU_RELRO)"

.PHONY: all clean token check 64bit static max_vuln