from flask import Flask, render_template, request
from werkzeug.utils import secure_filename 
import os
import zipfile
from threading import Thread
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
db = SQLAlchemy(app)

class FileContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300)) 

ALLOWED_EXTENSION = set(['zip'])
app.config['UPLOAD_FOLDER'] = 'uploads'

#pengecekan file degan menggunakan rsplit
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        file = request.files['file']

        if 'file' not in request.files:
            return render_template('upload.html')

        if file.filename == '':
            return render_template('upload.html')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            
            #ekstrak file
            with zipfile.ZipFile('uploads'+'//'+filename) as zf:
                zf.extractall('uploads')

                #melihat isi file zip
                filezip = zf.namelist()
                z = ("; ".join(filezip))

                #insert isi file zip ke db
                newFile = FileContent(name=z)
                db.session.add(newFile)
                db.session.commit()
                            
            return 'file ' + filename +' di simpan' + ' <a href="/upload">kembali</a>'

    return render_template('upload.html')
    threads = []
    for i in range(1):
        threads.append(Thread(target=upload))
        threads[-1].start()
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)