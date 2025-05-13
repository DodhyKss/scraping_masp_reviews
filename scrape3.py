import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===== Konfigurasi =====
CAFE_NAMES = [
    "Ardan Masogi Coffeeshop Tamalanrea"
]
MAX_REVIEWS = 50

# ===== Setup Selenium =====
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

all_data = []

for cafe_name in CAFE_NAMES:
    print(f"\n📍 Scraping: {cafe_name}")
    try:
        driver.get("https://www.google.com/maps")
        time.sleep(3)

        search_box = wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
        search_box.clear()
        search_box.send_keys(cafe_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)

        # Ambil nama dan alamat dari hasil Google Maps
        try:
            place_title = wait.until(EC.presence_of_element_located((By.XPATH, '//h1[contains(@class,"fontHeadlineLarge")]'))).text
        except:
            place_title = cafe_name

        try:
            address = wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(@data-item-id,"address")]/div'))).text
        except:
            address = "Alamat tidak ditemukan"

        print(f"📍 Nama di Maps: {place_title}")
        print(f"📫 Alamat: {address}")

        # Klik tab ulasan
        try:
            ulasan_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Ulasan")]')))
            ulasan_tab.click()
        except:
            ulasan_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Ulasan")]')))
            ulasan_tab.click()
        time.sleep(3)

        # Temukan kontainer review
        scrollable_div = None
        possible_xpaths = [
            '//div[@aria-label][div[contains(@class, "jftiEf")]]',
            '//div[contains(@class, "DxyBCb") and contains(@class, "kA9KIf")]',
            '//div[@role="main"]//div[contains(@class, "DxyBCb")]'
        ]

        for xpath in possible_xpaths:
            try:
                scrollable_div = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                break
            except:
                continue

        if not scrollable_div:
            print("⚠️ Tidak menemukan kontainer scroll review.")
            continue

        # Scroll review
        prev_count = 0
        while True:
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
            review_elements = driver.find_elements(By.XPATH, '//div[contains(@class,"jftiEf")]')
            if len(review_elements) >= MAX_REVIEWS or len(review_elements) == prev_count:
                break
            prev_count = len(review_elements)

        print(f"📦 Ulasan terkumpul: {len(review_elements)}")
        review_data = []

        for r in review_elements[:MAX_REVIEWS]:
            try:
                reviewer = r.find_element(By.CLASS_NAME, "d4r55").text
                rating = r.find_element(By.CLASS_NAME, "kvMYJc").get_attribute("aria-label")
                text = r.find_element(By.CLASS_NAME, "wiI7pd").text
                review_data.append({
                    "reviewer": reviewer,
                    "rating": rating,
                    "text": text
                })
            except Exception as e:
                print(f"⚠️ Gagal ambil salah satu review: {e}")
                continue

        cafe_result = {
            "searched_name": cafe_name,
            "place_name": place_title,
            "address": address,
            "reviews": review_data
        }
        all_data.append(cafe_result)

        # Simpan data per kafe
        filename = f"{place_title.replace(' ', '_')}_reviews.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(cafe_result, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"❌ Error saat scraping {cafe_name}: {e}")
        continue

# Simpan semua data ke satu file
with open("all_cafes_reviews.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

driver.quit()
print("\n🎉 Selesai scraping semua kafe!")
