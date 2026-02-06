# 📌 HƯỚNG DẪN CÀI ĐẶT & CHẠY HỆ THỐNG CHATBOT

## 1. Giới thiệu

Dự án này là một **hệ thống chatbot** sử dụng:

* **Embedding** để xử lý ngữ nghĩa
* **Qdrant** làm vector database
* **MinIO** để lưu trữ dữ liệu
* **Streamlit** để chạy giao diện chatbot

Hệ thống cho phép ingest dữ liệu, tạo embeddings và truy vấn thông tin thông minh.

---

## 2. Yêu cầu hệ thống

### Phần cứng

* **RAM**: Tối thiểu 8GB (khuyến nghị 16GB)
* **GPU**: Khuyến nghị GPU NVIDIA để tăng tốc quá trình embedding (không bắt buộc)

### Phần mềm

* **Hệ điều hành**: Windows
* **Python**: 3.11

---

## 3. Cấu trúc thư mục project

Cấu trúc thư mục đề xuất cho project như sau:

```text
project-root/
│── app.py                     # Ứng dụng chatbot (Streamlit)
│── utils.py                   # Các hàm tiện ích dùng chung
│── chunks_to_minio.py         # Chia nhỏ dữ liệu & upload lên MinIO
│── ingest_to_qdrant.py        # Tạo embedding & lưu vào Qdrant
│── requirements.txt           # Danh sách thư viện Python
│── README.md                  # Hướng dẫn cài đặt & sử dụng              
│── .env                       # File mẫu biến môi trường
│
├── data/
│   ├── raw/                   # Dữ liệu đầu vào (PDF, DOCX, TXT, ...)
│
├── models/
│   └── embedding/             # Embedding model tải từ Hugging Face
│     
│
├── qdrant_data/               # Thư mục chứa Qdrant executable & dữ liệu
│   ├── qdrant.exe
│   └── storage/
│
├── minio_data/                # Thư mục chứa MinIO executable & dữ liệu
│   ├── minio.exe
│   └── data/
│
```

## 3. Tải source code

Clone trực tiếp repository từ GitHub:

```bash
git clone https://github.com/Yiehh1/Chatbot
cd Chatbot
```

---

## 4. Cài đặt thư viện Python

Mở terminal (Command Prompt / PowerShell), di chuyển vào thư mục đã giải nén và chạy:

```bash
pip install -r requirements.txt
```

---

## 5. Cấu hình biến môi trường

Tuỳ chỉnh file **.env** trong thư mục gốc của project và cập nhật API key của bạn:

```env
# API keys
GEMINI_API_KEY="api_key_cua_ban"
```

⚠️ **Lưu ý:** Không chia sẻ file `.env` lên GitHub.

---

## 6. Tải & khởi động các dịch vụ backend

### 6.1 Tải file thực thi Qdrant

* Truy cập trang release chính thức của Qdrant
* Tải file **qdrant.exe** (phù hợp với Windows)
* Giải nén và đặt vào thư mục ví dụ:

```
qdrant_data/
```

Chạy Qdrant:

```bash
qdrant.exe
```

---

### 6.2 Tải file thực thi MinIO

* Truy cập trang chính thức của MinIO
* Tải file **minio.exe** cho Windows
* Đặt file vào thư mục ví dụ:

```
minio_data/
```

Chạy MinIO:

```bash
minio server .
```

📌 **Lưu ý:**

* Qdrant và MinIO phải **chạy liên tục** trong suốt quá trình sử dụng chatbot.

---

## 7. Tải embedding model & xử lý dữ liệu

### 7.1 Tải embedding model

Hệ thống sử dụng embedding model từ Hugging Face:

```
https://huggingface.co/huyydangg/DEk21_hcmute_embedding
```

Bạn tải model về máy và cấu hình đường dẫn model trong project nếu cần.

---

## 8. Xử lý dữ liệu & xây dựng cơ sở tri thức

### 7.1 Chuẩn bị dữ liệu

* Chuẩn bị tài liệu cần ingest
* Đặt các file vào thư mục:

```
data/raw/
```

---

### 7.2 Chia nhỏ dữ liệu & lưu vào MinIO

Chạy lệnh:

```bash
python chunks_to_minio.py
```

---

## 9. Tạo embeddings & lưu vào Qdrant

Thực thi lệnh:

```bash
python ingest_to_qdrant.py
```

---

## 10. Chạy ứng dụng chatbot

Khởi động giao diện chatbot bằng Streamlit:

```bash
streamlit run app.py
```

Sau khi chạy thành công, mở trình duyệt và truy cập địa chỉ được Streamlit cung cấp (thường là `http://localhost:8501`).

---

## 11. Ghi chú

* Đảm bảo Qdrant và MinIO đang chạy trước khi ingest dữ liệu hoặc sử dụng chatbot
* Kiểm tra đúng phiên bản Python (3.11)
* Nếu gặp lỗi thư viện, thử tạo virtual environment để tránh xung đột

---

## 12. Tác giả & bản quyền

Dự án phục vụ mục đích nghiên cứu và phát triển nội bộ.

---

✅ **Hoàn tất cài đặt!** Bạn có thể bắt đầu sử dụng chatbot 🚀
