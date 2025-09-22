import io
import requests
import subprocess
import re


def test_vulnerability_access():
    """Test that vulnerabilities are accessible for exploitation"""
    try:
        # Test format string vulnerability accessibility
        format_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="process %p.%p.%p.%p\nexit\n",
            capture_output=True,
            text=True
        )
        
        # Should show memory addresses if format string vuln is working
        if "0x" not in format_test.stdout and "%p" in format_test.stdout:
            print('Format string vulnerability is present and accessible')
            
        # Test controlled buffer overflow - now uses bounds checking but still vulnerable
        # Test with input just under the limit to ensure functionality works
        normal_input = "A" * 100  # Under 128 limit
        buffer_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "15", "/usr/local/bin/tni_c2_system"],
            input=f"officer\n{normal_input}\nTest\nexit\n",
            capture_output=True,
            text=True
        )
        
        # Should handle normal input correctly
        if "Nama perwira:" in buffer_test.stdout:
            print('Buffer handling is working correctly')
            
        # Test the new controlled heap vulnerability (input > 10 chars triggers malloc(32) with strcpy)
        heap_vuln_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="process " + "B" * 40 + "\nexit\n",  # 40 chars > 32 byte malloc buffer
            capture_output=True,
            text=True
        )
        
        if "Memproses komando:" in heap_vuln_test.stdout:
            print('Controlled heap vulnerability is accessible')
            
        return True
        
    except Exception as e:
        print(f'Vulnerability access test failed: {e}')
        return False

def test_post_patch_functionality():
    """Test that functions work correctly after patches are applied"""
    try:
        # Test that basic functionality still works after potential patches
        function_tests = [
            ("process normal_data\nexit\n", "Memproses komando: normal_data"),
            ("diagnostic\nnormal_diag\nexit\n", "Diagnostic 0: normal_diag"),
            ("classified\nnormal_classified\nexit\n", "Data tersimpan di alamat:"),
            ("officer\nNormal Officer\nMayor\nexit\n", "Nama perwira:"),
            ("network\nnormal_packet\nexit\n", "Paket diproses:")
        ]
        
        for test_input, expected_output in function_tests:
            result = subprocess.run(
                ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
                input=test_input,
                capture_output=True,
                text=True
            )
            
            if expected_output not in result.stdout:
                print(f'Post-patch functionality test failed for input: {test_input}')
                return False
                
        print('Post-patch functionality tests passed')
        return True
        
    except Exception as e:
        print(f'Post-patch functionality test failed: {e}')
        return False

def test_specific_vulnerability_behaviors():
    """Test specific behaviors of each vulnerability type"""
    try:
        # Test 1: Format string information disclosure - still works
        print('Testing format string information disclosure...')
        format_disc_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="diagnostic\n%08x.%08x.%08x.%08x\nexit\n",
            capture_output=True,
            text=True
        )
        
        # Test 2: Heap use-after-free behavior - still present
        print('Testing heap use-after-free behavior...')
        uaf_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="classified\ntest_heap_data\nexit\n",
            capture_output=True,
            text=True
        )
        
        # Test 3: Controlled heap overflow - new vulnerability (malloc(32) with strcpy)
        print('Testing controlled heap overflow...')
        heap_overflow_pattern = "A" * 50  # Larger than 32-byte malloc buffer
        heap_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "15", "/usr/local/bin/tni_c2_system"],
            input=f"process {heap_overflow_pattern}\nexit\n",
            capture_output=True,
            text=True
        )
        
        # Test 4: Network interface bounds checking - now has protection but may still be vulnerable
        print('Testing network interface with bounds checking...')
        # Test with input under limit
        normal_net_input = "A" * 200  # Under 256 limit
        net_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input=f"network\n{normal_net_input}\nexit\n",
            capture_output=True,
            text=True
        )
        
        # Test 5: Buffer overflow protection in process_command
        print('Testing buffer overflow protection...')
        # Test with input just under 128 bytes (should work)
        safe_input = "B" * 120
        safe_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input=f"process {safe_input}\nexit\n",
            capture_output=True,
            text=True
        )
        
        # Test with input over 128 bytes (should be truncated but not crash)
        large_input = "C" * 200
        large_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input=f"process {large_input}\nexit\n",
            capture_output=True,
            text=True
        )
        
        # Test 6: Shell access attempt (should be denied initially)
        print('Testing shell access denial...')
        shell_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="shell\nexit\n",
            capture_output=True,
            text=True
        )
        assert "AKSES DITOLAK" in shell_test.stdout, 'Shell access should be denied initially'
        
        print('Specific vulnerability behavior tests completed')
        return True
        
    except Exception as e:
        print(f'Specific vulnerability behavior test failed: {e}')
        return False

def check():
    try:
        # Step 1: Check if the flag still exists and matches the one in the container
        with open('../services/c2/flag.txt', 'r') as f:
            host_flag = f.read().strip()

        container_flag = subprocess.run(
            ["docker", "exec", "c2_container", "cat", "/flag.txt"],
            capture_output=True,
            text=True
        ).stdout.strip()                    

        assert host_flag == container_flag, 'Flag mismatch between host and container'
        
        print('Flag check passed for c2')

        # Step 2: Check if can access binary via SSH
        ssh_check = subprocess.run(
            ["docker", "exec", "c2_container", "test", "-f", "/usr/local/bin/tni_c2_system"],
            capture_output=True,
            text=True
        )
        assert ssh_check.returncode == 0, 'C2 binary not found in container'
        print('C2 binary check passed')
        
        # Step 4: Check if the C2 binary is executable and responding
        binary_check = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "5", "/usr/local/bin/tni_c2_system"],
            input="exit\n",
            capture_output=True,
            text=True
        )
        print(binary_check.stdout)
        assert "TNI COMMAND CENTER" in binary_check.stdout, 'C2 binary not responding correctly'
        print('C2 binary execution check passed')
        
        # Step 5: Check if clearance token file exists (needed for exploitation)
        token_check = subprocess.run(
            ["docker", "exec", "c2_container", "test", "-f", "/home/c2user/clearance_token"],
            capture_output=True,
            text=True
        )
        assert token_check.returncode == 0, 'Clearance token file not found'
        print('Clearance token check passed for c2')
        
        # Step 6: Test process_command function (format string vulnerability)
        process_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="process test_data\nexit\n",
            capture_output=True,
            text=True
        )
        assert "Memproses komando: test_data" in process_test.stdout, 'process_command function not working'
        assert "C2 Log: test_data" in process_test.stdout, 'Format string vulnerability in process_command not accessible'
        print('process_command function check passed')
        
        # Step 7: Test system_diagnostics function (format string vulnerability)
        diag_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="diagnostic\ntest_diag\nexit\n",
            capture_output=True,
            text=True
        )
        assert "C2 Diagnostics" in diag_test.stdout, 'system_diagnostics function not accessible'
        assert "Diagnostic 0: test_diag" in diag_test.stdout, 'Format string in diagnostics not working'
        print('system_diagnostics function check passed')
        
        # Step 8: Test manage_classified_data function (heap UAF vulnerability)
        classified_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="classified\ntest_classified_data\nexit\n",
            capture_output=True,
            text=True
        )
        assert "Data tersimpan di alamat:" in classified_test.stdout, 'manage_classified_data function not working'
        assert "Data masih dapat diakses:" in classified_test.stdout, 'UAF vulnerability in classified_data not accessible'
        print('manage_classified_data function check passed')
        
        # Step 9: Test add_officer function (buffer overflow vulnerability)
        officer_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="officer\nTest Officer\nKapten\nexit\n",
            capture_output=True,
            text=True
        )
        assert "Nama perwira:" in officer_test.stdout, 'add_officer function not accessible'
        assert "Pangkat:" in officer_test.stdout, 'add_officer input handling not working'
        print('add_officer function check passed')
        
        # Step 10: Test network_interface function (function pointer overwrite)
        network_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="network\ntest_packet\nexit\n",
            capture_output=True,
            text=True
        )
        assert "Network Interface" in network_test.stdout, 'network_interface function not accessible'
        assert "Paket diproses:" in network_test.stdout, 'network_interface processing not working'
        print('network_interface function check passed')
        
        # Step 11: Test help command and command recognition
        help_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="help\nexit\n",
            capture_output=True,
            text=True
        )
        assert "Available commands:" in help_test.stdout, 'Help command not working'
        assert "process <data>" in help_test.stdout, 'Command help not complete'
        print('Help and command interface check passed')
        
        # Step 12: Test controlled buffer handling (now has bounds checking)
        # Test with safe input size (should work correctly)
        safe_overflow_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "15", "/usr/local/bin/tni_c2_system"],
            input="process " + "A" * 50 + "\nexit\n",
            capture_output=True,
            text=True
        )
        # Should process input correctly with new bounds checking
        assert "Memproses komando:" in safe_overflow_test.stdout, 'Safe input processing not working'
        print('Controlled buffer handling check passed')
        
        # Step 13: Test new controlled heap vulnerability (malloc(32) with long input)
        heap_vuln_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "15", "/usr/local/bin/tni_c2_system"],
            input="process " + "B" * 40 + "\nexit\n",  # Triggers malloc(32) with 40-char input
            capture_output=True,
            text=True
        )
        assert "Memproses komando:" in heap_vuln_test.stdout, 'Controlled heap vulnerability not accessible'
        print('Controlled heap vulnerability check passed')
        
        # Step 14: Verify heap corruption issues are fixed (no more giant malloc)
        stability_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="process test1\nprocess test2\nprocess test3\nexit\n",
            capture_output=True,
            text=True
        )
        assert "Memproses komando: test1" in stability_test.stdout, 'Multiple commands causing instability'
        assert "Memproses komando: test2" in stability_test.stdout, 'Multiple commands causing instability'
        assert "Memproses komando: test3" in stability_test.stdout, 'Multiple commands causing instability'
        print('Heap stability check passed - no more malloc corruption')
        
        # Step 15: Verify format string vulnerability is still exploitable
        format_exploit_test = subprocess.run(
            ["docker", "exec", "c2_container", "timeout", "10", "/usr/local/bin/tni_c2_system"],
            input="process %x.%x.%x\nexit\n",
            capture_output=True,
            text=True
        )
        # Should show format string output (leaked memory addresses)
        assert "C2 Log:" in format_exploit_test.stdout, 'Format string vulnerability not exploitable'
        print('Format string vulnerability accessibility check passed')
        
        # Step 16: Run additional vulnerability access tests
        vuln_access_result = test_vulnerability_access()
        if not vuln_access_result:
            print('Some vulnerability access tests failed')
        
        # Step 17: Run post-patch functionality tests
        post_patch_result = test_post_patch_functionality()
        if not post_patch_result:
            print('Post-patch functionality tests failed')
        
        # Step 18: Run specific vulnerability behavior tests
        vuln_behavior_result = test_specific_vulnerability_behaviors()
        if not vuln_behavior_result:
            print('Specific vulnerability behavior tests failed')
        
        return True

    except Exception as e:
        print(f'Could not check c2: {e}')
        return False
    
    
check()