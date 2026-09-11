import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from ocr_vietnamese import VietnameseOCR
from api_processor import genai_api

app = FastAPI()
@app.get("/")
def home():
    return {"message": "Server FastAPI dang hoat dong!"}

# Bổ sung CORS cho phép Frontend gọi API (kể cả file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ocr = None

def get_ocr():
    global ocr
    if ocr is None:
        ocr = VietnameseOCR()
    return ocr


@app.get("/")
async def root_health_check():
    return {"status": "ok", "message": "Contract Analyzer API is running"}


@app.post("/api/analyze-contract")
async def analyze_contract(file: UploadFile = File(...)):
    # Lưu file tạm an toàn trên cả Windows/Linux
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        # OCR lấy text
        ocr_instance = get_ocr()
        ocr_result = ocr_instance.get_full_text(temp_path)

        # Phân tích qua Gemini
        analysis = genai_api(ocr_result)

        # Trả về kết quả thực tế từ Gemini
        return JSONResponse(content=analysis)
    except Exception as e:
        print("Lỗi trong quá trình xử lý:", e)
        return JSONResponse(
            status_code=500,
            content={"error": f"Lỗi xử lý Gemini/OCR: {str(e)}"}
        )
    finally:
        # Dọn dẹp file tạm
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)