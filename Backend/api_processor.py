from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv

load_dotenv()

def genai_api(data):
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        api_key = api_key.strip("'\" \t\r\n")

    if not api_key or api_key == "your_api_key_here":
        raise ValueError("Chưa cấu hình GEMINI_API_KEY hợp lệ! Vui lòng tạo file .env trong thư mục Backend với nội dung: GEMINI_API_KEY=AIzaSy...")

    client = genai.Client(api_key=api_key)
    prompt = f"""
    Đánh giá hợp đồng này và trả về JSON với cấu trúc:
    {{
      "score": <int từ 0 đến 100, trong đó 100 là an toàn tuyệt đối, dưới 50 là rủi ro cao>,
      "summary": <string: Tóm tắt tổng quan tình trạng hợp đồng và các rủi ro chính>,
      "clauses": [
        {{
          "title": <string: Tên loại điều khoản hoặc cảnh báo bẫy pháp lý>,
          "location": <string: Vị trí trong hợp đồng, ví dụ: Điều 4.2 hoặc Dòng 12>,
          "text": <string: Trích dẫn nguyên văn điều khoản trong hợp đồng>,
          "analysis": <string: Nhận định chi tiết của AI và trích dẫn điều luật bảo vệ người thuê>,
          "risk_level": <string: "high" nếu bất lợi nghiêm trọng, "medium" nếu mập mờ, "info" nếu cần lưu ý>
        }}
      ]
    }}
    Văn bản hợp đồng:
    {data}
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    text = response.text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    return json.loads(text)
