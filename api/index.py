from pdf2docx import Converter
from flask import Flask, request, render_template, send_file
import os
import threading
import time
import schedule

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_files(pdf_path, docx_path):
    time.sleep(60)  # Wait for 1 minute before deleting the files
    os.remove(pdf_path)
    os.remove(docx_path)

def schedule_file_deletion(pdf_path, docx_path):
    thread = threading.Thread(target=delete_files, args=(pdf_path, docx_path))
    thread.start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_pdf_to_word():
    if 'pdf_file' not in request.files:
        return 'No file part'
    
    file = request.files['pdf_file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file and allowed_file(file.filename):
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)
        
        word_path = os.path.splitext(pdf_path)[0] + '.docx'
        pdf_to_word(pdf_path, word_path)
        
        # Schedule file deletion after 1 minute
        schedule_file_deletion(pdf_path, word_path)
        
        return download_link(word_path)
    else:
        return 'Invalid file type'

def pdf_to_word(pdf_path, word_path):
    cv = Converter(pdf_path)
    cv.convert(word_path, start=0, end=None)
    cv.close()

def download_link(file_path):
    return f'<a href="/download/{os.path.basename(file_path)}">Download your file</a>'

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    schedule.run_pending()  # Run any scheduled tasks
    app.run(debug=True)
