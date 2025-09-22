# -----------------------------------------------------------------------------
# run.py - Main Flask Application Router
# -----------------------------------------------------------------------------
# File ini bertindak sebagai titik masuk utama dan router untuk aplikasi web.
# Tugasnya adalah menerima permintaan HTTP dan mendelegasikannya ke modul
# yang sesuai untuk diproses.
# -----------------------------------------------------------------------------

from flask import Flask, request, render_template, send_from_directory
from markupsafe import Markup
import os

# Impor fungsi handler dari setiap modul fitur.
# Setiap modul bertanggung jawab atas satu fungsionalitas spesifik.
from modules.disk_analyzer import handle_disk_analysis
from modules.pdf_analyzer import handle_pdf_analysis
from modules.png_analyzer import handle_png_analysis

# Inisialisasi aplikasi Flask
app = Flask(__name__)

FLAG = open('/flag.txt', 'r').read().strip()
# Kunci rahasia diperlukan oleh Flask untuk mengelola sesi dan pesan flash.
# Dalam aplikasi nyata, ini harus berupa string yang kompleks dan acak.
app.secret_key = 'd43f8b1a9e7c2d5e6a1b9f0c8d7e6a5b'

# --- Definisi Rute (Routes) ---

@app.route('/')
def index():
    return render_template('index.html')

# Tambahkan rute GET untuk setiap alat
@app.route('/disk')
def disk_page():
    return render_template('disk_analyzer.html')

@app.route('/pdf')
def pdf_page():
    return render_template('pdf_analyzer.html')

@app.route('/png')
def png_page():
    return render_template('png_analyzer.html')

@app.route('/static/downloads/<path:filename>')
def download_file(filename):
    """Rute aman untuk menyajikan file yang telah dibuat."""
    # Path absolut ke direktori unduhan di dalam kontainer
    download_directory = os.path.abspath('/app/static/downloads')
    return send_from_directory(download_directory, filename, as_attachment=True)


@app.route('/analyze/disk', methods=['POST'])
def analyze_disk_route():
    """
    Rute untuk fitur Penganalisis Disk Image.
    Menerima file yang diunggah melalui metode POST, memanggil handler,
    dan me-render hasilnya.
    """
    html_result = handle_disk_analysis(request)
    # Me-render template utama dan menyisipkan hasil analisis disk
    # ke dalam variabel 'disk_result' di dalam template.
    try:
        return render_template('disk_analyzer.html', disk_result=Markup(html_result))
    except Exception as render_e:
        safe_render_e = Markup.escape(str(render_e))
        error_message = f"""
            <h3>Rendering Error:</h3>
            <div class="result-box">
                <pre>Terjadi error saat me-render template: {safe_render_e}</pre>
            </div>
            """
        return render_template('disk_analyzer.html', disk_result=Markup(error_message))


@app.route('/analyze/pdf', methods=['POST'])
def analyze_pdf_route():
    """
    Rute untuk fitur Penganalisis Plugin PDF.
    Menerima file yang diunggah, memanggil handler, dan me-render hasilnya.
    """
    result = handle_pdf_analysis(request)
    # Me-render template utama dan menyisipkan hasil analisis PDF
    # ke dalam variabel 'pdf_result'.
    return render_template('pdf_analyzer.html', pdf_result=result)

@app.route('/analyze/png', methods=['POST'])
def analyze_png_route():
    # Panggil handler, yang sekarang mengembalikan sebuah dictionary
    result_dict = handle_png_analysis(request)
    # Kirim dictionary tersebut ke template
    return render_template('png_analyzer.html', png_result=result_dict)


# --- Titik Masuk Eksekusi Aplikasi ---

if __name__ == '__main__':
    """
    Blok ini hanya akan dieksekusi jika file ini dijalankan secara langsung
    (bukan diimpor sebagai modul). Ini adalah cara standar untuk memulai
    server pengembangan Flask.
    - host='0.0.0.0' membuat server dapat diakses dari luar kontainer.
    - port=5000 adalah port standar yang akan kita expose.
    """
    app.run(host='0.0.0.0', port=5000)