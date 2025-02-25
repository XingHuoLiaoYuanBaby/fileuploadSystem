from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import os
import shutil
import hashlib

app = FastAPI()

# 配置API路径前缀
API_PREFIX = "/dky"

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置上传目录
UPLOAD_DIR = "uploads"
TEMP_DIR = "temp"

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# 配置静态文件服务
app.mount("/static", StaticFiles(directory="."), name="static")

# 根目录报告404
@app.get("/")
async def redirect_root():
    return JSONResponse({"message": "404 not found"})

# 路径错误报告404
@app.middleware("http")
async def catch_all_middleware(request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        return JSONResponse({"message": "404 not found, please check your path"})
    return response

@app.get("/api/prefix")
async def get_api_prefix():
    return JSONResponse({"prefix": API_PREFIX})

@app.get(f"{API_PREFIX}/")
async def read_root():
    return FileResponse("index.html")

@app.get(f"{API_PREFIX}/download.html")
async def read_download_page():
    return FileResponse("download.html")

@app.post(f"{API_PREFIX}/upload/chunk")
async def upload_chunk(
    file: UploadFile = File(...),
    chunk_number: int = Form(...),
    total_chunks: int = Form(...),
    file_id: str = Form(...),
    original_filename: str = Form(...),
):
    if not all([chunk_number is not None, total_chunks is not None, file_id]):
        raise HTTPException(status_code=400, detail="Missing parameters")
    
    try:
        chunk_number = int(chunk_number)
        total_chunks = int(total_chunks)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid chunk number or total chunks")

    # 创建文件ID对应的临时目录
    chunk_dir = os.path.join(TEMP_DIR, file_id)
    os.makedirs(chunk_dir, exist_ok=True)

    # 保存分片
    chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_number}")
    with open(chunk_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 检查是否所有分片都已上传
    uploaded_chunks = os.listdir(chunk_dir)
    if len(uploaded_chunks) == total_chunks:
        # 合并文件，使用原始文件名
        final_path = os.path.join(UPLOAD_DIR, original_filename)
        with open(final_path, "wb") as final_file:
            for i in range(total_chunks):
                chunk_path = os.path.join(chunk_dir, f"chunk_{i}")
                with open(chunk_path, "rb") as chunk:
                    shutil.copyfileobj(chunk, final_file)

        # 清理临时文件
        shutil.rmtree(chunk_dir)
        return JSONResponse({"status": "complete", "file_path": final_path})

    return JSONResponse({"status": "chunk_uploaded", "chunk": chunk_number})

@app.get(f"{API_PREFIX}/upload/status/{{file_id}}")
async def check_upload_status(file_id: str):
    chunk_dir = os.path.join(TEMP_DIR, file_id)
    if not os.path.exists(chunk_dir):
        return JSONResponse({"status": "not_found"})

    uploaded_chunks = os.listdir(chunk_dir)
    return JSONResponse({
        "status": "in_progress",
        "uploaded_chunks": len(uploaded_chunks)
    })

@app.get(f"{API_PREFIX}/files")
async def list_files():
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            file_path = os.path.join(UPLOAD_DIR, filename)
            file_stat = os.stat(file_path)
            files.append({
                "name": filename,
                "size": file_size,
                "upload_time": file_stat.st_mtime
            })
    return JSONResponse({"files": files})

@app.get(f"{API_PREFIX}/download/{{filename}}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.delete(f"{API_PREFIX}/files/{{filename}}")
async def delete_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        os.remove(file_path)
        return JSONResponse({"status": "success", "message": "File deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print(f"服务将启动在 http://127.0.0.1:8888{API_PREFIX}")
    uvicorn.run(app, host="0.0.0.0", port=8888)