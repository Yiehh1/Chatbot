from minio import Minio
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize
import json
from tqdm import tqdm
import os
from dotenv import load_dotenv

load_dotenv()

# Clients
mc = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=os.getenv("MINIO_SECURE", "False").lower() == "true"
)

qd = QdrantClient(host=os.getenv("QDRANT_HOST"), port=int(os.getenv("QDRANT_PORT")))
mdl = SentenceTransformer(os.getenv("EMBEDDING_MODEL_PATH"))

col = os.getenv("QDRANT_COLLECTION")

# Tạo collection nếu chưa có
if not qd.collection_exists(col):
    qd.create_collection(
        collection_name=col,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )
    print(f"Tạo collection {col}")

obs = mc.list_objects(os.getenv("MINIO_BUCKET"))
pts = []

print("Embedding...")
for o in tqdm(obs, desc="Processing"):
    d = mc.get_object(os.getenv("MINIO_BUCKET"), o.object_name)
    ck = json.loads(d.read())
    
    txt = tokenize(ck["content"])
    vec = mdl.encode(txt).tolist()

    pts.append(PointStruct(
        id=ck["metadata"]["chunk_id"],
        vector=vec,
        payload={
            "content": ck["content"],
            "title": ck["metadata"]["title"],
            "images": ck.get("images", []),
            "source": ck["metadata"]["source"]
        }
    ))

if pts:
    qd.upsert(collection_name=col, points=pts)
    print(f"Upsert {len(pts)} points thành công!")