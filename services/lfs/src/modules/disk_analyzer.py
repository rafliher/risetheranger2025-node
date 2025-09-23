import os
import subprocess
import uuid
import shutil
from flask import render_template_string
from markupsafe import escape

BLACKLIST_FILE = '/app/blacklists/template_blacklist.txt'
UPLOAD_FOLDER = '/app/uploads'
MAX_FILE_SIZE = 6 * 1024 * 1024
ALLOWED_EXTENSION = '.dd'
FLAG = open('/flag.txt', 'r').read().strip()

def onlyoneortwolenchars(s):
    return len(s) <= 2

def get_blacklist():
    try:
        with open(BLACKLIST_FILE, 'r') as f:
            lines = f.read().splitlines()
            valid_lines = lines[:5] 
            processed_lines = []
            for line in valid_lines:
                clean_line = line.strip()[:10]
                if onlyoneortwolenchars(clean_line):
                    continue
                processed_lines.append(clean_line)
            return processed_lines
    except FileNotFoundError:
        return

def get_string_quota():
    try:
        with open(BLACKLIST_FILE, 'r') as f:
            lines = f.read().splitlines()
            valid_lines = lines[:5]
            quota = 0
            for line in valid_lines:
                lng = len(line.strip()[:10])
                clean_line = line.strip()[:10]
                if onlyoneortwolenchars(clean_line):
                    continue
                line_quota = (lng * 3) + ((10 - lng) * 88)
                quota += line_quota
            if quota == 0:
                quota = 880
            return quota
    except FileNotFoundError:
        return

def handle_disk_analysis(request):
    FLAG = open('/flag.txt', 'r').read().strip()
    file = request.files.get('disk_image')
    

    if not file or not file.filename:
        return {'error': "No file selected."}
    if not file.filename.lower().endswith(ALLOWED_EXTENSION):
        return {'error': f"Invalid file type. Only {ALLOWED_EXTENSION} files are accepted."}
    
    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_FILE_SIZE:
        return {'error': f"File size exceeds the {MAX_FILE_SIZE / 1024 / 1024}MB limit."}
    file.seek(0)

    session_id = str(uuid.uuid4())
    temp_dir = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(temp_dir, exist_ok=True)
    filepath = os.path.join(temp_dir, file.filename)
    file.save(filepath)


    template_string = ""

    try:

        try:
            exif_process = subprocess.run(['exiftool', filepath], capture_output=True, text=True, timeout=10)
            exif_data = exif_process.stdout if exif_process.returncode != 0 else f"ExifTool Error: {exif_process.stderr}"

            safe_exif_data = escape(exif_data)
            template_string += f"""
                <h3 class="text-2xl font-bold text-white mt-8 mb-4">ExifTool Metadata:</h3>
                <pre class="bg-slate-950/70 p-6 rounded-lg border border-slate-700 font-mono text-sm overflow-x-auto whitespace-pre-wrap break-words">{safe_exif_data}</pre>
            """
            render_template_string(template_string)
        except Exception as exif_e:
            safe_exif_e = escape(str(exif_e))
            template_string += f"""
                <h3 class="text-2xl font-bold text-white mt-8 mb-4">ExifTool Metadata:</h3>
                <pre class="bg-slate-950/70 p-6 rounded-lg border border-slate-700 font-mono text-sm overflow-x-auto whitespace-pre-wrap break-words">Gagal menjalankan ExifTool: {safe_exif_e}</pre>
            """

        partition_info_str = ""
        ls_result_str = ""

        try:
            mmls_process = subprocess.run(['mmls', filepath], capture_output=True, text=True, timeout=10)
            if mmls_process.returncode != 0:
                raise ValueError(f"Gagal membaca tabel partisi: {mmls_process.stderr.strip()}")
            
            partition_info_str = mmls_process.stdout
            start_sector = None
            sector_size = 512
            for line in mmls_process.stdout.splitlines():
                if "units are in" in line.lower() and "-byte sectors" in line.lower():
                    try:
                        size_str = line.lower().split('-byte sectors')[0].split()[-1]
                        sector_size = int(size_str)
                    except (ValueError, IndexError): pass
                elif "ntfs" in line.lower() or "0x07" in line:
                    parts = line.split()
                    if len(parts) > 2 and parts[2].isdigit():
                        start_sector = int(parts[2])
                        break
            
            if start_sector is None:
                raise ValueError("Tidak ditemukan partisi NTFS yang valid.")

            offset = start_sector * sector_size
            with open(filepath, 'rb') as f:
                f.seek(offset + 3)
                signature = f.read(4)
                if signature != b'NTFS':
                    raise ValueError(f"Signature NTFS tidak valid di partisi (ditemukan: {signature!r}).")

            fls_process = subprocess.run(['fls', '-r', '-o', str(start_sector), filepath], capture_output=True, text=True, timeout=20)
            if fls_process.returncode != 0:
                raise RuntimeError(f"Gagal mendaftar file di partisi: {fls_process.stderr.strip()}")
            
            ls_result_str = fls_process.stdout

        except (ValueError, RuntimeError) as partition_e:
            partition_info_str = f"Gagal membaca sebagai disk berpartisi. Mencoba sebagai raw filesystem...\n\nAlasan: {partition_e}"
            
            try:
                with open(filepath, 'rb') as f:
                    f.seek(3)
                    signature = f.read(4)
                    if signature != b'NTFS':
                        raise ValueError(f"File tidak memiliki signature NTFS yang valid di awal file (ditemukan: {signature!r}).")

                fls_process = subprocess.run(['fls', '-r', '-o', '0', filepath], capture_output=True, text=True, timeout=20)
                if fls_process.returncode != 0:
                    raise RuntimeError(f"Gagal mendaftar file: {fls_process.stderr.strip()}")
                
                ls_result_str = fls_process.stdout
            except (ValueError, RuntimeError) as raw_e:
                ls_result_str = f"Analisis Gagal. Tidak bisa membaca file sebagai disk berpartisi ataupun raw filesystem.\n\nError terakhir: {raw_e}"

        try:
            safe_partition_info = escape(partition_info_str)
            template_string += f"""
                <h3 class="text-2xl font-bold text-white mt-8 mb-4">Partition Information:</h3>
                <pre class="bg-slate-950/70 p-6 rounded-lg border border-slate-700 font-mono text-sm overflow-x-auto whitespace-pre-wrap break-words">{safe_partition_info}</pre>
            """
            render_template_string(template_string)
        except Exception as partition_render_e:
            safe_partition_render_e = escape(str(partition_render_e))
            template_string += f"""
                <h3 class="text-2xl font-bold text-white mt-8 mb-4">Partition Information:</h3>
                <pre>Gagal me-render informasi partisi: {safe_partition_render_e}</pre><
            """

        
        if ls_result_str and not ls_result_str.startswith("Analisis Gagal"):
            blacklist = get_blacklist()
            safe_ls_output = ls_result_str
            if blacklist:
                for word in blacklist:
                    if word: safe_ls_output = safe_ls_output.replace(word, '')
            ls_result_str = safe_ls_output
            string_quota = get_string_quota()
            if len(ls_result_str) > string_quota:
                raise ValueError("Daftar file terlalu panjang berdasarkan kuota yang diizinkan dari blacklist.")

        try:
            ls_res = f"""
                <h3 class="text-2xl font-bold text-white mt-8 mb-4">File Listing:</h3>
                <pre class="bg-slate-950/70 p-6 rounded-lg border border-slate-700 font-mono text-sm overflow-x-auto whitespace-pre-wrap break-words">{ls_result_str}</pre>
            """
            render_template_string(ls_res)
            template_string += ls_res
        except Exception as ls_render_e:
            safe_ls_render_e = escape(str(ls_render_e))
            template_string += f"""
                <h3 class="text-2xl font-bold text-white mt-8 mb-4">File Listing:</h3>
                <pre class="bg-slate-950/70 p-6 rounded-lg border border-slate-700 font-mono text-sm overflow-x-auto whitespace-pre-wrap break-words">Gagal me-render daftar file: {safe_ls_render_e}</pre>
            """

        try:
            return render_template_string(template_string)
        except Exception as ssti_e:
            safe_ssti_e = escape(str(ssti_e))

            safe_original_template = escape(template_string)

            final_template = f"""
                <h3>Analysis Output (Render Failed)</h3>
                <div class="result-box">
                    <pre>{safe_original_template}</pre>
                </div>
                
                <hr>
                
                <div class="callout callout-danger">
                    <h4>Rendering Error Details</h4>
                    <pre>{safe_ssti_e}</pre>
                </div>
            """
            return final_template
    except Exception as e:
        safe_e = escape(str(e))
        template_string += f"""
            <h3>Fatal Error:</h3>
            <div class="result-box"><pre>Terjadi error kritis: {safe_e}</pre></div>
        """
        return render_template_string(template_string)

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)