from transformers import MarianMTModel, MarianTokenizer
from gtts import gTTS
import torch
import os
import json
# Bước 1: Đọc nội dung từ JSON
with open("output.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    ##input_text = data.get("content", "")

if not data:
    print("❌ File JSON không có nội dung để dịch.")
    exit()


# Chọn mô hình dịch từ Đức sang Anh
model_name = "Helsinki-NLP/opus-mt-de-en"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


# Tokenize và dịch
for i, article in enumerate(data):
    input_text = article["content"]
inputs = tokenizer([input_text], return_tensors="pt", padding=True, truncation=True)
translation = model.generate(**inputs)
translated_text = tokenizer.batch_decode(translation, skip_special_tokens=True)[0]

print("📌 Bản dịch:", translated_text)

# Chuyển thành giọng nói
tts = gTTS(translated_text, lang='en')
tts.save("output.mp3")

# Phát âm thanh trên local (Windows/macOS/Linux)
if os.name == 'nt':  # Windows
    os.system("start output.mp3")
else:  # macOS/Linux
    os.system("mpg321 output.mp3")

