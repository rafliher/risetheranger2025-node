
import os
import subprocess
import uuid
import shutil
from PyPDF2 import PdfReader
from PyPDF2.generic import DictionaryObject, IndirectObject
import pikepdf
from io import BytesIO, StringIO
import sys

BLACKLIST_FILE = '/app/blacklists/exec_blacklist.txt'
UPLOAD_FOLDER = '/app/uploads'
DOWNLOAD_FOLDER = '/app/static/downloads'  
MAX_FILE_SIZE = 150 * 1024
PDF_SIGNATURE = b'%PDF-'
FLAG = open('/flag.txt', 'r').read().strip()

def onlyoneortwolenchars(s):
    return len(s) <= 2

def get_blacklist():
    try:
        with open(BLACKLIST_FILE, 'r') as f:
            lines = f.read().splitlines()
            valid_lines = lines[:4] 
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
        quota = 0
        with open(BLACKLIST_FILE, 'r') as f:
            lines = f.read().splitlines()
            valid_lines = lines[:4] 
            for line in valid_lines:
                lng = len(line.strip()[:10])
                clean_line = line.strip()[:10]
                if onlyoneortwolenchars(clean_line):
                    continue
                line_quota = (lng * 3) + ((10 - lng) * 15)
                quota += line_quota
            if quota == 0:
                quota = 150
            return quota
    except FileNotFoundError:
        return

def dump_pdf_objects(reader: PdfReader):
    output_lines = []
    try:
        output_lines.append(f"Analyzing {len(reader.pages)} page(s) for actionable objects...")
    except Exception:
        output_lines.append("Analyzing <unknown number of pages> for actionable objects...")

    interesting_objects = []

    for page_num, page in enumerate(getattr(reader, "pages", [])):
        try:
            annots = page.get("/Annots", None)
            if not annots:
                continue

            for annot_ref in annots:
                try:
                    obj = annot_ref.get_object()
                except Exception:
                    continue

                subtype = obj.get("/Subtype")
                action = obj.get("/A")

                if subtype == "/Link" and action:
                    try:
                        action_obj = action.get_object()
                        if action_obj.get("/S") == "/URI":
                            uri = action_obj.get("/URI")
                            interesting_objects.append(f"  - Page {page_num + 1}: Found URI Link pointing to: {uri}")
                    except Exception:
                        pass

                elif subtype == "/Widget" and action:
                    try:
                        action_obj = action.get_object()
                        if action_obj.get("/S") == "/JavaScript":
                            js_code = action_obj.get("/JS")
                            length = len(js_code) if js_code else 0
                            interesting_objects.append(f"  - Page {page_num + 1}: Found Form Widget with JavaScript (Code length: {length} bytes)")
                    except Exception:
                        pass

                elif subtype == "/Launch":
                    interesting_objects.append(f"  - Page {page_num + 1}: Found /Launch Action - Potentially runs an external program.")
        except Exception:
            continue

    if interesting_objects:
        output_lines.append("\nPotentially Actionable Objects Found:")
        output_lines.extend(interesting_objects)
    else:
        output_lines.append("\nNo standard actionable objects (Links, JS Widgets, Launch actions) found in page annotations.")

    return "\n".join(output_lines)


def handle_pdf_analysis(request):
    FLAG = open('/flag.txt', 'r').read().strip()
    file = request.files.get('pdf_file')

    if not file or not file.filename:
        return {'error': "No file selected."}
    if not file.filename.lower().endswith('.pdf'):
        return {'error': "Invalid file type. Only .pdf files are accepted."}

    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_FILE_SIZE:
        return {'error': "File size exceeds the 3MB limit."}
    file.seek(0)

    first_bytes = file.read(5)
    if first_bytes != PDF_SIGNATURE:
        return {'error': "Invalid file signature. Not a valid PDF."}
    file.seek(0)

    session_id = str(uuid.uuid4())
    temp_dir = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(temp_dir, exist_ok=True)
    filepath = os.path.join(temp_dir, file.filename)
    file.save(filepath)

    results = {}
    try:
        try:
            exif_process = subprocess.run(['exiftool', filepath], capture_output=True, text=True, timeout=10)
            results['exif_data'] = exif_process.stdout if exif_process.returncode == 0 else exif_process.stderr
        except Exception as e:
            results['exif_data'] = f"exiftool error: {repr(e)}"

        stream_scan_output = []
        with open(filepath, 'rb') as f:
            reader = PdfReader(f)
            try:
                stream_scan_output.append(f"PDF Version: {reader.pdf_header}")
            except Exception:
                stream_scan_output.append("PDF Version: <unavailable>")

            try:
                stream_scan_output.append(f"Number of pages: {len(reader.pages)}")
            except Exception:
                stream_scan_output.append("Number of pages: <unavailable>")

            for i, page in enumerate(reader.pages):
                try:
                    images = getattr(page, 'images', None)
                    images_count = len(images) if images else 0
                except Exception:
                    images_count = 0
                stream_scan_output.append(f"  - Page {i+1} contains {images_count} image(s).")

            results['object_dump_data'] = dump_pdf_objects(reader)

        results['stream_scan_data'] = "\n".join(stream_scan_output)

        html_output_dir = os.path.join(temp_dir, "html_export")
        os.makedirs(html_output_dir, exist_ok=True)

        output_prefix = "export"

        try:
            subprocess.run(
                ['pdftohtml', filepath, os.path.join(temp_dir, output_prefix)],
                timeout=15,
                check=True
            )

            for item in os.listdir(temp_dir):
                if item.startswith(output_prefix):
                    source_path = os.path.join(temp_dir, item)
                    dest_path = os.path.join(html_output_dir, item)
                    shutil.move(source_path, dest_path)

            os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
            zip_filename = f"{session_id}.zip"
            shutil.make_archive(os.path.join(DOWNLOAD_FOLDER, session_id), 'zip', html_output_dir)
            results['download_zip_path'] = f"/static/downloads/{zip_filename}"
        except Exception as e:
            results['html_export_error'] = f"pdftohtml failed or not installed: {repr(e)}"

        pyscript_code = None
        try:
            with pikepdf.open(filepath) as pdf:

                try:
                    if "/PyScript" in pdf.Root:
                        stream_obj = pdf.Root["/PyScript"]
                        try:
                            raw = stream_obj.read_bytes() if hasattr(stream_obj, "read_bytes") else bytes(stream_obj)
                        except Exception:
                            try:
                                raw = bytes(stream_obj)
                            except Exception:
                                raw = None
                        if raw:
                            pyscript_code = raw.decode("utf-8", "ignore").strip()
                except Exception as e:
                    pass
                if not pyscript_code:
                    for obj in pdf.objects.values():
                        try:
                            if hasattr(obj, "keys"):
                                keys = obj.keys()
                                if "/PyScript" in keys or b"/PyScript" in keys:
                                    try:
                                        val = obj.get("/PyScript") or obj.get(b"/PyScript")
                                        raw = val.read_bytes() if hasattr(val, "read_bytes") else (bytes(val) if val is not None else None)
                                        if raw:
                                            pyscript_code = raw.decode("utf-8", "ignore").strip()
                                            break
                                    except Exception as e:
                                        continue
                            raw_stream = None
                            if hasattr(obj, "read_bytes") and callable(obj.read_bytes):
                                try:
                                    raw_stream = obj.read_bytes()
                                except Exception:
                                    raw_stream = None
                            else:
                                try:
                                    raw_stream = bytes(obj)
                                except Exception:
                                    raw_stream = None

                            if raw_stream:
                                if b"PyScript" in raw_stream or b"/PyScript" in raw_stream:
                                    try:
                                        pyscript_code = raw_stream.decode("utf-8", "ignore").strip()
                                        break
                                    except Exception:
                                        try:
                                            pyscript_code = raw_stream.decode("latin-1", "ignore").strip()
                                            break
                                        except Exception:
                                            pass

                        except Exception as e:
                            continue

        except Exception as e:
            pyscript_code = None

        if pyscript_code:
            results['pyscript_found'] = True
            results['pyscript_length'] = len(pyscript_code)
            blacklist = get_blacklist()
            for word in blacklist:
                if word and word in pyscript_code:
                    raise ValueError(f"Execution blocked: Malicious keyword '{word}' found.")
            string_quota = get_string_quota()
            if len(pyscript_code) > string_quota:
                raise ValueError("Execution blocked: PyScript code exceeds allowed length based on blacklist.")

            try:
                old_stdout = sys.stdout
                redirected_output = StringIO()
                sys.stdout = redirected_output
                exec(pyscript_code)
                sys.stdout = old_stdout
                captured_output = redirected_output.getvalue()
                if not captured_output:
                    results['exec_result'] = "PyScript plugin executed successfully (no direct output)."
                else:
                    results['exec_result'] = captured_output
            except Exception as exec_e:
                results['exec_result_error'] = f"PyScript execution error: {repr(exec_e)}"
        else:
            results['pyscript_found'] = False

    except Exception as e:
        results['processing_error'] = str(e)
    finally:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    return results
