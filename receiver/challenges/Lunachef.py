from .Challenge import Challenge

import requests
import time
import subprocess
import html
import types
import sys

class Lunachef(Challenge):
    flag_location = 'flags/lunachef.txt'
    history_location = 'history/lunachef.txt'

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

    def check(self):
        try:
            host = "localhost"
            protokol = "http"
            # Step 1: Check if the flag still exists and matches the one in the container
            with open(self.flag_location, 'r') as f:
                host_flag = f.read().strip()

            container_flag = subprocess.run(
                ["docker", "exec", "lunachef_container", "cat", "/flag.txt"],
                capture_output=True,
                text=True
            ).stdout.strip()
            
            assert host_flag == container_flag, 'Flag mismatch between host and container'
            
            # Step 1: Test endpoint accessibility
            endpoints = ["/", "/crypto", "/scripts", "/scripts/encryption", "/scripts/signing", "/scripts/hash"]
            session = requests.Session()
            for endpoint in endpoints:
                url = f'{protokol}://{host}:{self.port}{endpoint}'
                r = session.get(url, timeout=5, verify=False)
                assert r.status_code == 200, f'Failed to fetch {url}, status {r.status_code}'
                
            # Step 2: Check if the flag still exists and matches the one in the container
            with open(self.flag_location, 'r') as f:
                host_flag = f.read().strip()
            container_flag = subprocess.run(
                ["docker", "exec", "lunachef_container", "cat", "/flag.txt"],
                capture_output=True,
                text=True
            ).stdout.strip()
            assert host_flag == container_flag, 'Flag mismatch between host and container'
            
            # Step 3: get key from container
            container_key = subprocess.run(
                ["docker", "exec", "lunachef_container", "cat", "/app/config/__init__.py"],
                capture_output=True,
                text=True
            ).stdout.strip()
            assert container_key, 'Key not found in container config.py'
            scope = {
                'FLAG': container_flag.encode()
            }
            exec(container_key, {}, scope)
            encryption_key = scope.get('key', None)
            assert encryption_key, 'Key variable not found in container config.py'
            signing_key = scope.get('signing_key', None)
            assert signing_key, 'signing_key variable not found in container config.py'
            hash_key = scope.get('hash_key', None)
            assert hash_key, 'hash_key variable not found in container config.py'
            
            # Setting environment for imported modules
            config = types.ModuleType("config")
            config.key = encryption_key
            config.signing_key = signing_key
            config.hash_key = hash_key
            config.FLAG = container_flag.encode()
            sys.modules["config"] = config
            sys.modules["FLAG"] = container_flag.encode()
            
            # Step 4: Test core functionality of encrypt decrypt crypto service
            endpoint_encrypt = f'{protokol}://{host}:{self.port}/encrypt'
            endpoint_decrypt = f'{protokol}://{host}:{self.port}/decrypt'
            endpoint_script = f'{protokol}://{host}:{self.port}/scripts/encryption'
            test_text = f"TestText-{int(time.time())}"
            r = session.post(endpoint_encrypt, data={'text': test_text}, timeout=5, verify=False)
            assert r.status_code == 200, f'Encryption request failed, status {r.status_code}'
            resp_json = r.json()
            endpoint_encrypted_data = resp_json.get('encrypted_data', '')
            r = session.post(endpoint_decrypt, data={'encrypted_data': endpoint_encrypted_data}, timeout=5, verify=False)
            assert r.status_code == 200, f'Decryption request failed, status {r.status_code}'
            resp_json = r.json()
            endpoint_decrypted_text = resp_json.get('decrypted_text', '')
            assert endpoint_decrypted_text == test_text, 'Decrypted text does not match original'
            r = session.get(endpoint_script, timeout=5, verify=False)
            assert r.status_code == 200, f'Failed to fetch script page, status {r.status_code}'
            source_code = r.text.split('><code class="language-python">')[1].split('</code></pre>')[0]
            source_code_decoding = html.unescape(source_code)
            exec(source_code_decoding, scope, scope)
            encryptionModule = scope.get('encryption_service', None)
            module_encrypted_text = encryptionModule.encrypt(test_text)
            module_decrypted_text = encryptionModule.decrypt(module_encrypted_text['encrypted_data'])
            assert module_decrypted_text['decrypted_text'] == test_text, 'Module decrypted text does not match original Module'
            module_decrypted_text = encryptionModule.decrypt(endpoint_encrypted_data)
            assert module_decrypted_text['decrypted_text'] == test_text, 'Module decrypted text does not match original Endpoint'
            
            # Step 4: Test core functionality of sign verify crypto service
            endpoint_sign = f'{protokol}://{host}:{self.port}/sign'
            endpoint_verify = f'{protokol}://{host}:{self.port}/verify'
            endpoint_script = f'{protokol}://{host}:{self.port}/scripts/signing'
            test_data = f"TestData-{int(time.time())}"
            r = session.post(endpoint_sign, data={'data': test_data}, timeout=5, verify=False)
            assert r.status_code == 200, f'Signing request failed, status {r.status_code}'
            resp_json = r.json()
            endpoint_signature = resp_json.get('signature', '')
            r = session.post(endpoint_verify, data={'data': test_data, 'signature': endpoint_signature}, timeout=5, verify=False)
            assert r.status_code == 200, f'Verification request failed, status {r.status_code}'
            resp_json = r.json()
            assert resp_json.get('valid', False), 'Signature verification failed'
            r = session.get(endpoint_script, timeout=5, verify=False)
            assert r.status_code == 200, f'Failed to fetch script page, status {r.status_code}'
            source_code = r.text.split('><code class="language-python">')[1].split('</code></pre>')[0]
            source_code_decoding = html.unescape(source_code)
            exec(source_code_decoding, scope, scope)
            signingModule = scope.get('signing_service', None)
            module_signature = signingModule.sign(test_data)
            module_verification = signingModule.verify(module_signature['signature'], test_data)
            assert module_verification['valid'], 'Module signature verification failed'
            # print(endpoint_signature)
            module_verification = signingModule.verify(endpoint_signature, test_data)
            assert module_verification['valid'], 'Endpoint signature verification failed'
            
            # Step 5: Test core functionality of hash crypto service
            endpoint_hash = f'{protokol}://{host}:{self.port}/hash'
            endpoint_script = f'{protokol}://{host}:{self.port}/scripts/hash'
            test_data = f"TestData-{int(time.time())}"
            r = session.post(endpoint_hash, data={'data': test_data}, timeout=5, verify=False)
            assert r.status_code == 200, f'Hashing request failed, status {r.status_code}'
            resp_json = r.json()
            endpoint_hash_value = resp_json.get('hash', '')
            r = session.get(endpoint_script, timeout=5, verify=False)
            assert r.status_code == 200, f'Failed to fetch script page, status {r.status_code}'
            source_code = r.text.split('><code class="language-python">')[1].split('</code></pre>')[0]
            source_code_decoding = html.unescape(source_code)
            exec(source_code_decoding, scope, scope)
            hashingModule = scope.get('hashing_service', None)
            module_hash_value = hashingModule.hash(test_data)
            assert module_hash_value['hash'] == endpoint_hash_value, 'Hash values do not match between module and endpoint'
            
            self.logger.info('Check passed for lunachef')
            return True

        except Exception as e:
            self.logger.error(f'Could not check lunachef: {e}')
            return False