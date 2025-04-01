import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import json
import time

#driver 
driver = None
def init_driver():
    global driver  
    if driver is None:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver= webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver
def close_driver():
    global driver
    if driver is not None:
        driver.quit()
        driver = None

# Kiểm tra xem trang có phải tĩnh không
def is_static_page(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            static_text = " ".join([p.text.strip() for p in soup.find_all("p") if p.text.strip()])
            return static_text
    except requests.exceptions.RequestException:
        return None
    return None

# Kiểm tra trang JavaScript
def scrape_with_selenium(url):
    global driver
    try:
        if driver is None:
            driver = init_driver()
        else:
            driver.get(url)  # Tải lại trang nếu driver đã được khởi tạo
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "p"))
            )

        js_text = " ".join([p.text.strip() for p in driver.find_elements(By.TAG_NAME, 'p') if p.text.strip()])
        
        return js_text
    except Exception as e:
        print(f"❌ Error loading page with Selenium: {e}")
        return None
   

# Lưu văn bản vào file JSON
def save_text_to_json(article_obj, filename="output.json"):
    try: 
        # Đọc dữ liệu cũ
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
            data = []
    # Kiểm tra xem URL đã tồn tại chưa
    existing_urls = {item["url"] for item in data}
    if article_obj["url"] in existing_urls:
        print(f"⏭ Đã tồn tại: {article_obj['url']}")
        return
    # Thêm bài mới
    data.append(article_obj)
    
    with open(filename,"w", encoding = "utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print (f"📌 Saved to {filename}")  


#Hàm phân loại xem cái nào cần dùng BeutifulSoup cào, cái nào cần dùng Selenium
def classify_scraping_method(url):
    static_text = is_static_page(url)
    if static_text:
        print("\n📌 This website is STATIC. Using BeautifulSoup to scrape content.")
        return static_text
    else:
        print("\n⚠ This website may use JavaScript. Checking with Selenium...")
        dynamic_text = scrape_with_selenium(url)
        if dynamic_text:
            print(f"\n🚀 Website {url} requires JavaScript. Content length: {len(dynamic_text)} characters")
            return dynamic_text
        else:
            print("\n❌ I can't load the website.")
            return None
# Hàm làm sạch văn bản
def clean_repetitive_text(text, min_repeat=3, min_paragraph_length=50):
    if not text:
        return text
    # Bước 1: Làm sách từ lặp liên tiếp
    words = text.split(" ")
    cleaned_words = []
    last_word = None
    repeat_count = 1
        
    for word in words:
        if word == last_word:
            repeat_count += 1
        else:
            repeat_count = 1
            last_word = word
            
        if repeat_count <= min_repeat:
            cleaned_words.append(word)
        
    intermediate_text = ' '.join(cleaned_words) 

    # Bước 2: Xử lý đoạn văn lặp lại
    paragraphs = [p.strip() for p in intermediate_text.split('\n') if p.strip()]
    unique_paragraphs = []
    seen_paragraphs = set() 
    for para in paragraphs:
        # Chỉ xem xét các đoạn đủ dài
        if len(para.split()) >= min_paragraph_length:
            # Chuẩn hóa đoạn văn để so sánh (bỏ qua khoảng trắng thừa, chuyển thành chữ thường)
            normalized = ' '.join(para.lower().split())
            if normalized not in seen_paragraphs:
                seen_paragraphs.add(normalized)
                unique_paragraphs.append(para)
        else:
            unique_paragraphs.append(para)  # Giữ lại các đoạn ngắn
    # Bước 3: Loại bỏ các mẫu quảng cáo/thông báo lặp lại
    common_patterns = [
        "cookie policy", "privacy policy", "terms of service",
        "please enable javascript", "we use cookies",
        "đang tải...", "loading...", "click để xem thêm"
    ]
    final_paragraphs = []
    for para in unique_paragraphs:
        if not any(pattern.lower() in para.lower() for pattern in common_patterns):
            final_paragraphs.append(para)
    
    return '\n'.join(final_paragraphs)
       
# Hàm chính
if __name__ == "__main__":
    try: 
        with open("article_links.json", "r", encoding="utf-8") as f:
            url = json.load(f)

        for item in url:
            input_url = item["content"]
            text = classify_scraping_method(input_url)
            if text:
                cleaned_text = clean_repetitive_text(text)
                
        
                article_obj = {
                        "url": input_url,
                        "content": cleaned_text
                }
        
                save_text_to_json(article_obj)  # ✅ Ghi từng bài sau khi scrape
            else:
                print(f"❌ Failed to scrape the article: {input_url}")

        print("📌 Finished scraping all articles.")
    finally:
        close_driver()  # Đóng driver khi hoàn thành


