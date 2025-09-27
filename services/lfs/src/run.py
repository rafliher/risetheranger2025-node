from flask import Flask, request, render_template, send_from_directory
from markupsafe import Markup
import os


from modules.disk_analyzer import handle_disk_analysis
from modules.pdf_analyzer import handle_pdf_analysis
from modules.png_analyzer import handle_png_analysis


app = Flask(__name__, static_folder='assets')


app.secret_key = 'd43f8b1a9e7c2d5e6a1b9f0c8d7e6a5b'



@app.route('/')
def index():
    return render_template('index.html')

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
    download_directory = os.path.abspath('/app/static/downloads')
    return send_from_directory(download_directory, filename, as_attachment=True)


@app.route('/analyze/disk', methods=['POST'])
def analyze_disk_route():

    html_result = handle_disk_analysis(request)

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

    result = handle_pdf_analysis(request)
    return render_template('pdf_analyzer.html', pdf_result=result)

@app.route('/analyze/png', methods=['POST'])
def analyze_png_route():
    result_dict = handle_png_analysis(request)
    return render_template('png_analyzer.html', png_result=result_dict)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)