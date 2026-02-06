import os
import json
import io
from minio import Minio
from utils import extract_sections_and_images
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# MinIO client
cli = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=os.getenv("MINIO_SECURE", "False").lower() in ("true", "1", "yes")
)

BK = os.getenv("MINIO_BUCKET", "ctu-quyche")

# Thư mục chứa file docx
RF = "data/raw"
if not os.path.exists(RF):
    raise FileNotFoundError(f"Không tìm thấy thư mục {RF}")

# Lấy danh sách file docx
df = [f for f in os.listdir(RF) if f.lower().endswith(('.docx', '.doc'))]
df.sort()

print(f"Tìm thấy {len(df)} file .docx:")
for f in df:
    print("  →", f)
print("-" * 60)

gc = 0  # global chunk counter

for fn in tqdm(df, desc="Xử lý file DOCX"):
    fp = os.path.join(RF, fn)
    
    print(f"\nĐang xử lý: {fn}")
    try:
        ck = extract_sections_and_images(fp)
        print(f"   → Tạo được {len(ck)} chunk + ảnh")

        sb = os.path.splitext(fn)[0]  # source base

        # Upload từng chunk
        for i, c in enumerate(ck, start=1):
            gc += 1
            on = f"{sb}_{i:03d}.json"

            d = json.dumps(c, ensure_ascii=False, indent=2).encode('utf-8')

            cli.put_object(
                bucket_name=BK,
                object_name=on,
                data=io.BytesIO(d),
                length=len(d),
                content_type="application/json"
            )
        print(f"   → Đã upload {len(ck)} chunk cho {sb} (tổng: {gc})")

    except Exception as e:
        print(f"   → LỖI khi xử lý {fn}: {e}")

print("\nHOÀN TẤT! Tổng cộng đã xử lý:")
print(f"   • {len(df)} file .docx")
print(f"   • {gc} chunk được upload lên MinIO")
print(f"   • Ảnh đã tự động upload vào bucket: {os.getenv('MINIO_IMAGE_BUCKET')}")