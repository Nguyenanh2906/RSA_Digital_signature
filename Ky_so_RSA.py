from flask import Flask, request, send_file, redirect, flash, Response, get_flashed_messages
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import os
from jinja2 import Template

app = Flask(__name__)
app.secret_key = 'rsa-app-secret'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Tạo khóa RSA
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# HTML giao diện
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>RSA File Signer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #ffe0f0, #ffd6ec);
            font-family: 'Segoe UI', sans-serif;
        }
        .card {
            border-radius: 1rem;
            box-shadow: 0 6px 20px rgba(255, 105, 180, 0.25);
            margin-bottom: 2rem;
        }
        .btn-rose {
            background-color: #ff69b4;
            border: none;
            color: white;
        }
        .btn-rose:hover {
            background-color: #ff3399;
        }
        .text-rose {
            color: #d63384;
        }
        .section-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #d63384;
        }
        .alert-info {
            background-color: #ffe4f0;
            color: #d63384;
            border-color: #f5c2d7;
        }
        a {
            text-decoration: none;
        }
    </style>
</head>
<body>
<div class="container py-5">
    <h1 class="text-center mb-5 text-rose">💖 Ứng dụng Ký số RSA </h1>

    {% if messages %}
        <div class="alert alert-info text-center">{{ messages|safe }}</div>
    {% endif %}

    <div class="card p-4">
        <div class="section-title mb-3">📤 Ký số file</div>
        <form action="/sign" method="post" enctype="multipart/form-data">
            <div class="mb-3">
                <label class="form-label">Chọn file cần ký:</label>
                <input type="file" name="file" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-rose w-100">🔏 Ký và tải về</button>
        </form>
    </div>

    {% if download_links %}
        <div class="card p-4">
            <div class="section-title mb-2">📁 Kết quả ký số và tải xuống:</div>
            {{ download_links|safe }}
        </div>
    {% endif %}

    <div class="card p-4">
        <div class="section-title mb-3">📥 Xác minh chữ ký</div>
        
        {% if last_signed_file %}
            <div class="mb-3">
                <p class="text-muted">⬇️ Tải file đã ký và public key:</p>
                <ul>
                    <li><a href="/download/{{ last_signed_file }}" class="link-success">📄 File gốc</a></li>
                    <li><a href="/download/{{ last_signed_file }}.sig" class="link-danger">🔏 Chữ ký</a></li>
                    <li><a href="/download/{{ last_signed_file }}.pub" class="link-info">🔑 Public key</a></li>
                </ul>
                <p class="text-muted">📝 Vui lòng tải về và chọn lại các file phía dưới để xác minh.</p>
            </div>
        {% endif %}
        
        <form action="/verify" method="post" enctype="multipart/form-data">
            <div class="mb-3">
                <label class="form-label">File gốc:</label>
                <input type="file" name="file" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Chữ ký:</label>
                <input type="file" name="signature" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Public Key:</label>
                <input type="file" name="public_key" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-rose w-100">✅ Xác minh chữ ký</button>
        </form>
    </div>

</div>
</body>
</html>
'''

@app.route('/')
def index():
    messages = '<br>'.join(get_flashed_messages())
    html = Template(HTML_TEMPLATE).render(messages=messages, download_links="", last_signed_file=None)
    return Response(html, mimetype='text/html')

@app.route('/sign', methods=['POST'])
def sign_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        flash("⚠️ Vui lòng chọn một file!")
        return redirect('/')

    filename = uploaded_file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(filepath)

    # Đọc nội dung và ký
    with open(filepath, 'rb') as f:
        data = f.read()

    signature = private_key.sign(
        data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )

    # Lưu chữ ký và public key
    sig_path = filepath + '.sig'
    pub_path = filepath + '.pub'

    with open(sig_path, 'wb') as f:
        f.write(signature)

    with open(pub_path, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    # Tạo liên kết tải file
    links = f'''
        <ul>
            <li><a href="/download/{filename}" class="link-success">📁 File gốc</a></li>
            <li><a href="/download/{filename}.sig" class="link-danger">🔏 Chữ ký</a></li>
            <li><a href="/download/{filename}.pub" class="link-info">🔑 Public key</a></li>
        </ul>
    '''

    html = Template(HTML_TEMPLATE).render(
        messages="✅ Ký số thành công! Vui lòng tải các file bên dưới.",
        download_links=links,
        last_signed_file=filename
    )
    return Response(html, mimetype='text/html')

@app.route('/verify', methods=['POST'])
def verify_signature():
    file = request.files['file']
    sig = request.files['signature']
    pub = request.files['public_key']

    if not (file and sig and pub):
        flash("⚠️ Vui lòng chọn đầy đủ file, chữ ký và public key!")
        return redirect('/')

    file_data = file.read()
    sig_data = sig.read()
    pub_data = pub.read()

    try:
        pubkey = serialization.load_pem_public_key(pub_data)
        pubkey.verify(sig_data, file_data,
                      padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                  salt_length=padding.PSS.MAX_LENGTH),
                      hashes.SHA256())
        flash("✅ Chữ ký HỢP LỆ.")
    except Exception:
        flash("❌ Chữ ký KHÔNG hợp lệ.")

    return redirect('/')

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
