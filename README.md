from flask import Flask, request, render_template_string, send_file
import rsa
import os
import requests

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

TEMPLATE = '''
<!doctype html>
<title>RSA Ký và Gửi File</title>
<h1>🔐 Ký & Xác minh</h1>
<form method=post enctype=multipart/form-data action="/sign">
  <p><input type=file name=file>
     <input type=submit value="Ký file">
</form>
{% if signed %}
  <p><b>Đã ký thành công!</b></p>
  <ul>
    <li><a href="/download/{{signed}}">File chữ ký (.sig)</a></li>
    <li><a href="/download/{{pubkey}}">Khóa công khai (.pem)</a></li>
  </ul>
{% endif %}

<hr>

<h2>✅ Xác minh chữ ký</h2>
<form method=post enctype=multipart/form-data action="/verify">
  <p>File gốc: <input type=file name=orig_file><br>
     File chữ ký: <input type=file name=sig_file><br>
     File public key: <input type=file name=pubkey_file><br>
     <input type=submit value="Xác minh">
</form>
{% if verify_result is not none %}
  <p><b>Kết quả:</b> {{ '✅ Hợp lệ' if verify_result else '❌ Không hợp lệ' }}</p>
{% endif %}

<hr>

<h2>🌐 Gửi File đến IP</h2>
<form method=post enctype=multipart/form-data action="/send">
  <p>Nhập IP người nhận (VD: http://192.168.1.100:5000/receive)</p>
  <input type=text name=receiver_url placeholder="http://...">
  <br><br>Chọn file gốc: <input type=file name=file>
  <br>File chữ ký: <input type=file name=sig_file>
  <br>File khóa công khai: <input type=file name=pubkey_file>
  <br><input type=submit value="Gửi">
</form>
{% if send_result %}
  <p>{{ send_result }}</p>
{% endif %}
'''

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TEMPLATE, signed=None, verify_result=None, send_result=None)

@app.route("/sign", methods=["POST"])
def sign_file():
    file = request.files['file']
    data = file.read()

    # Tạo khóa RSA
    pubkey, privkey = rsa.newkeys(2048)

    # Ký dữ liệu
    signature = rsa.sign(data, privkey, 'SHA-256')

    # Lưu file
    orig_filename = os.path.join(UPLOAD_FOLDER, file.filename)
    sig_filename = orig_filename + ".sig"
    pubkey_filename = orig_filename + ".pem"

    with open(orig_filename, "wb") as f: f.write(data)
    with open(sig_filename, "wb") as f: f.write(signature)
    with open(pubkey_filename, "wb") as f: f.write(pubkey.save_pkcs1())

    return render_template_string(TEMPLATE, signed=os.path.basename(sig_filename), pubkey=os.path.basename(pubkey_filename), verify_result=None, send_result=None)

@app.route("/verify", methods=["POST"])
def verify():
    orig_file = request.files['orig_file'].read()
    sig = request.files['sig_file'].read()
    pubkey_data = request.files['pubkey_file'].read()
    pubkey = rsa.PublicKey.load_pkcs1(pubkey_data)

    try:
        rsa.verify(orig_file, sig, pubkey)
        result = True
    except rsa.VerificationError:
        result = False

    return render_template_string(TEMPLATE, signed=None, verify_result=result, send_result=None)

@app.route("/send", methods=["POST"])
def send():
    receiver_url = request.form['receiver_url']
    files = {
        'file': request.files['file'],
        'sig_file': request.files['sig_file'],
        'pubkey_file': request.files['pubkey_file']
    }

    try:
        r = requests.post(receiver_url, files=files)
        result = "✅ Gửi thành công!" if r.status_code == 200 else "❌ Gửi thất bại!"
    except Exception as e:
        result = f"❌ Lỗi: {e}"

    return render_template_string(TEMPLATE, signed=None, verify_result=None, send_result=result)

@app.route("/receive", methods=["POST"])
def receive():
    for f in request.files.values():
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))
    return "Đã nhận file!", 200

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
