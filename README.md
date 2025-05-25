# 🔐 Ứng dụng Ký, Xác minh và Truyền File với RSA

## 📝 Giới thiệu hệ thống

Ứng dụng này mô phỏng quy trình ký số và xác minh chữ ký số bằng thuật toán RSA 2048-bit, đồng thời hỗ trợ truyền file qua mạng nội bộ. Hệ thống đảm bảo tính toàn vẹn và xác thực của dữ liệu bằng cách sử dụng cặp khóa công khai và khóa bí mật.

Ứng dụng phù hợp cho sinh viên, nhà phát triển và bất kỳ ai muốn hiểu rõ cơ chế hoạt động của chữ ký số trong bảo mật thông tin.


## ✨ Chức năng chính
-Tạo cặp khóa RSA
Tự động sinh cặp khóa công khai và bí mật (2048-bit) cho mỗi phiên ký file.

-Ký file
Cho phép chọn một file bất kỳ, hệ thống sẽ sử dụng khóa bí mật để tạo chữ ký số (.sig) và lưu khóa công khai (.pem) đi kèm.

-Xác minh chữ ký
Nhập vào file gốc, file chữ ký và file chứa khóa công khai để kiểm tra tính hợp lệ của chữ ký số.

-Truyền file qua mạng
Gửi đồng thời file gốc, chữ ký và public key đến địa chỉ IP và cổng của một ứng dụng khác đang chạy trong mạng nội bộ.


## Các bước cài đặt
### ⚙️ Hướng dẫn cài đặt
#### 📌 Yêu cầu
Python 3.x
Các thư viện
1.  **Cài đặt thư viện:**
    ```bash
    pip install Flask rsa requests Werkzeug 
    ```

2.  **Chạy ứng dụng:**
    ```bash
    rsa_digital_signature.py  ( Running on http:// (địa chỉ):5000)
    ```



## 🚀 Hướng dẫn sử dụng
# 1. **🔐 Ký file**:

1.1. Truy cập tab "Ký & Xác minh"

1.2. Chọn file bạn muốn ký.

1.3. Hệ thống sẽ:

- Tự động sinh khóa RSA.

- Tạo và lưu 3 file:

✅ File gốc

✅ File chữ ký số (.sig)

✅ File khóa công khai (.pem)

# 2. **✅ Xác minh chữ ký**

2.1. Truy cập tab "Ký & Xác minh"

2.2. Tải lên:

- File gốc

- File chữ ký

- File khóa công khai

2.3. Nhấn nút "Xác minh" để kiểm tra tính toàn vẹn và nguồn gốc file.

# 3. **🌐 Truyền file qua mạng**
3.1. Truy cập tab "Gửi File"

3.2. Nhập địa chỉ IP và cổng của máy nhận (máy đó phải đang chạy ứng dụng này).

3.3. Chọn và gửi:

- File gốc

- File chữ ký

- File khóa công khai





