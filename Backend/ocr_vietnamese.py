from pathlib import Path
from typing import List, Dict, Any

from paddleocr import PaddleOCR


class VietnameseOCR:
    """
    Vietnamese OCR using PaddleOCR 3.7.0.

    Pipeline:
        Image
          ↓
        PaddleOCR PP-OCRv3
          ↓
        Text detection + recognition
          ↓
        Extract Vietnamese text
    """

    def __init__(
        self,
        lang: str = "vi",
        ocr_version: str = "PP-OCRv3",
        device: str = "cpu",
    ):

        self.ocr = PaddleOCR(
            lang=lang,
            ocr_version=ocr_version,

            # Không cần xoay ảnh / tài liệu trong bài toán này
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,

            # CPU
            device=device,

            # Tắt MKL-DNN để tránh một số vấn đề
            # tương thích trên Windows.
            enable_mkldnn=False,
        )

    # =========================================================
    # 1. KIỂM TRA FILE ẢNH
    # =========================================================

    @staticmethod
    def validate_image(image_path: str) -> Path:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy file ảnh: {image_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Đường dẫn không phải là file: {image_path}"
            )

        supported_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".webp",
            ".tif",
            ".tiff",
        }

        if path.suffix.lower() not in supported_extensions:
            raise ValueError(
                f"Định dạng ảnh không được hỗ trợ: {path.suffix}"
            )

        return path

    # =========================================================
    # 2. CHẠY OCR
    # =========================================================

    def run_ocr(self, image_path: str):
        path = self.validate_image(image_path)

        # PaddleOCR 3.x hỗ trợ truyền trực tiếp path
        results = self.ocr.predict(str(path))

        return results

    # =========================================================
    # 3. TRÍCH XUẤT TEXT
    # =========================================================

    @staticmethod
    def extract_text(results) -> List[Dict[str, Any]]:
        extracted = []

        for result in results:
            result_json = result.json

            if isinstance(result_json, str):
                import json

                result_json = json.loads(result_json)

            data = result_json.get("res", result_json)

            texts = data.get("rec_texts", [])
            scores = data.get("rec_scores", [])

            for index, text in enumerate(texts):

                score = None

                if index < len(scores):
                    score = float(scores[index])

                extracted.append(
                    {
                        "text": str(text),
                        "score": score,
                    }
                )

        return extracted

    # =========================================================
    # 4. LẤY DANH SÁCH TEXT
    # =========================================================

    def get_text(self, image_path: str) -> List[str]:
        results = self.run_ocr(image_path)

        extracted = self.extract_text(results)

        return [
            item["text"]
            for item in extracted
            if item["text"].strip()
        ]

    # =========================================================
    # 5. LẤY TEXT + SCORE
    # =========================================================

    def get_text_with_scores(
        self,
        image_path: str
    ) -> List[Dict[str, Any]]:

        results = self.run_ocr(image_path)

        return self.extract_text(results)

    # =========================================================
    # 6. GỘP THÀNH MỘT ĐOẠN VĂN
    # =========================================================

    def get_full_text(self, image_path: str) -> str:

        texts = self.get_text(image_path)

        return "\n".join(texts)

    # =========================================================
    # 7. HÀM PROCESS CHÍNH
    # =========================================================

    def process(self, image_path: str) -> Dict[str, Any]:
        path = self.validate_image(image_path)

        results = self.run_ocr(str(path))

        extracted = self.extract_text(results)

        texts = [
            item["text"]
            for item in extracted
            if item["text"].strip()
        ]

        full_text = "\n".join(texts)

        return {
            "image": str(path),
            "texts": texts,
            "full_text": full_text,
            "results": extracted,
        }