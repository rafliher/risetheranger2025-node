from .Challenge import Challenge

import io
import requests
import random
import subprocess
import json

class C2(Challenge):
    flag_location = 'flags/c2.txt'
    history_location = 'history/c2.txt'

    def distribute(self, flag):
        try:
            with open(self.flag_location, 'w') as f:
                f.write(flag)
            
            with open(self.history_location, 'a') as f:
                f.write(flag + '\n')

            self.logger.info(f'Flag {flag} written to {self.flag_location}')
            return True

        except Exception as e:
            self.logger.error(f'Could not write flag to {self.flag_location}: {e}')
            return False

    def _run_c2(self, commands, timeout=10):
        if isinstance(commands, str):
            commands = [commands]
        cmd = [
            "docker",
            "exec",
            "-i",
            "c2_container",
            "timeout",
            str(timeout),
            "/usr/local/bin/tni_c2_system",
        ]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        input_str = "".join(c if c.endswith("\n") else c + "\n" for c in commands)
        try:
            stdout, stderr = proc.communicate(input=input_str, timeout=timeout + 2)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
        return stdout

    def check(self):
        try:
            # Step 1: Check if the flag still exists and matches the one in the container
            with open(self.flag_location, 'r') as f:
                host_flag = f.read().strip()

            container_flag = subprocess.run(
                ["docker", "exec", "c2_container", "cat", "/flag.txt"],
                capture_output=True,
                text=True
            ).stdout.strip()                    

            assert host_flag == container_flag, 'Flag mismatch between host and container'
            
            self.logger.info('Flag check passed for c2')

            # Step 2: Check if can access binary via SSH
            ssh_check = subprocess.run(
                ["docker", "exec", "c2_container", "test", "-f", "/usr/local/bin/tni_c2_system"],
                capture_output=True,
                text=True
            )
            assert ssh_check.returncode == 0, 'C2 binary not found in container'
            self.logger.info('C2 binary check passed')
            
            # Step 4: Check if the C2 binary is executable and responding
            binary_out = self._run_c2(["exit"], timeout=5)
            assert "TNI COMMAND CENTER" in binary_out, 'C2 binary not responding correctly'
            self.logger.info('C2 binary execution check passed')
            
            # Step 5: Check if clearance token file exists (needed for exploitation)
            token_check = subprocess.run(
                ["docker", "exec", "c2_container", "test", "-f", "/opt/clearance_token"],
                capture_output=True,
                text=True
            )
            assert token_check.returncode == 0, 'Clearance token file not found'
            self.logger.info('Clearance token check passed for c2')
            
            # Step 6: Test process_command function (format string vulnerability)
            process_out = self._run_c2(["process test_data", "exit"], timeout=10)
            assert "Memproses komando: test_data" in process_out, 'process_command function not working'
            assert "C2 Log: test_data" in process_out, 'Format string vulnerability in process_command not accessible'
            self.logger.info('process_command function check passed')
            
            # Step 7: Test system_diagnostics function (format string vulnerability)
            diag_out = self._run_c2(["diagnostic", "test_diag", "exit"], timeout=10)
            assert "C2 Diagnostics" in diag_out, 'system_diagnostics function not accessible'
            assert "Diagnostic 0: test_diag" in diag_out, 'Format string in diagnostics not working'
            self.logger.info('system_diagnostics function check passed')
            
            # Step 8: Test manage_classified_data function (heap UAF vulnerability)
            classified_out = self._run_c2(["classified", "test_classified_data", "exit"], timeout=10)
            assert "Data tersimpan di alamat:" in classified_out, 'manage_classified_data function not working'
            assert "Data masih dapat diakses:" in classified_out, 'UAF vulnerability in classified_data not accessible'
            self.logger.info('manage_classified_data function check passed')
            
            # Step 9: Test add_officer function (buffer overflow vulnerability)
            officer_out = self._run_c2(["officer", "Test Officer", "Kapten", "exit"], timeout=10)
            assert "Nama perwira:" in officer_out, 'add_officer function not accessible'
            assert "Pangkat:" in officer_out, 'add_officer input handling not working'
            self.logger.info('add_officer function check passed')
            
            # Step 10: Test network_interface function (function pointer overwrite)
            network_out = self._run_c2(["network", "test_packet", "exit"], timeout=10)
            assert "Network Interface" in network_out, 'network_interface function not accessible'
            assert "Paket diproses:" in network_out, 'network_interface processing not working'
            self.logger.info('network_interface function check passed')
            
            # Step 11: Test help command and command recognition
            help_out = self._run_c2(["help", "exit"], timeout=10)
            assert "Available commands:" in help_out, 'Help command not working'
            assert "process <data>" in help_out, 'Command help not complete'
            self.logger.info('Help and command interface check passed')
            
            # Step 12: Test controlled buffer handling (now has bounds checking)
            # Test with safe input size (should work correctly)
            safe_overflow_out = self._run_c2(["process " + "A" * 50, "exit"], timeout=15)
            # Should process input correctly with new bounds checking
            assert "Memproses komando:" in safe_overflow_out.stdout if hasattr(safe_overflow_out, 'stdout') else "Memproses komando:" in safe_overflow_out, 'Safe input processing not working'
            self.logger.info('Controlled buffer handling check passed')
            
            return True

        except Exception as e:
            self.logger.error(f'Could not check c2: {e}')
            return False
        