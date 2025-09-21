import os
import subprocess
from flask import render_template_string

BLACKLIST_FILE = '/app/blacklists/eval_blacklist.txt'
UPLOAD_FOLDER = '/app/uploads'
MAX_FILE_SIZE = 1 * 1024 * 1024  
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n' 
FLAG = open('/flag.txt', 'r').read().strip()

def get_blacklist():
    try:
        with open(BLACKLIST_FILE, 'r') as f:
            return f.read(150).splitlines()
    except FileNotFoundError:
        return

def handle_png_analysis(request):
    file = request.files.get('png_file')
    
    if not file or not file.filename:
        return {'error': "No file selected for upload."}

    if not file.filename.lower().endswith('.png'):
        return {'error': "Invalid file type. Only.png files are accepted."}

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    if file_size > MAX_FILE_SIZE:
        return {'error': f"File size exceeds the maximum limit of {MAX_FILE_SIZE / 1024 / 1024}MB."}
    file.seek(0) 

    header = file.read(8)
    if header!= PNG_SIGNATURE:
        return {'error': "Invalid file signature. The uploaded file is not a valid PNG."}
    file.seek(0) 


    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    results = {}
    try:
        exif_process = subprocess.run(['exiftool', filepath], capture_output=True, text=True, timeout=10)
        results['exif_data'] = exif_process.stdout if exif_process.returncode == 0 else exif_process.stderr

        pngcheck_process = subprocess.run(['pngcheck', '-v', filepath], capture_output=True, text=True, timeout=10)
        results['pngcheck_data'] = pngcheck_process.stdout if pngcheck_process.returncode == 0 else pngcheck_process.stderr

        content = open(filepath, 'rb').read()
        chunk_type = b'LFTD' 
        chunk_start = content.find(chunk_type)

        if chunk_start > 0:
            data_len_bytes = content[chunk_start - 4 : chunk_start]
            data_len = int.from_bytes(data_len_bytes, 'big')
            
            data_start = chunk_start + 4
            chunk_data = content[data_start : data_start + data_len].decode('utf-8', 'ignore')
            
            results['lftd_header_found'] = True
            
            blacklist = get_blacklist()
            for word in blacklist:
                if word and word in chunk_data:
                    raise ValueError(f"Execution blocked: Malicious keyword '{word}' found in LFTD chunk.")

            eval_output = eval(chunk_data, {"__builtins__": {}}, {})
            results['eval_result'] = str(eval_output) if eval_output is not None else "Code executed (no return value)."
        
    except Exception as e:
        results['processing_error'] = str(e)
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            
    return results