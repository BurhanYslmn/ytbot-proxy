import time
import random
import os
import zipfile
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

VIDEO_URL = "https://www.youtube.com/shorts/e2ouqeqZJnY"

def create_proxy_extension(proxy_address, auth):
    ip, port = proxy_address.split(":")
    user, pwd = auth.split(":")

    manifest_json = {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": ["proxy", "tabs", "unlimitedStorage", "storage", "<all_urls>", "webRequest", "webRequestBlocking"],
        "background": {
            "scripts": ["background.js"]
        }
    }

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{ip}",
                port: parseInt({port})
            }},
            bypassList: ["localhost"]
        }}
    }};
    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});
    chrome.webRequest.onAuthRequired.addListener(
        function(details) {{
            return {{
                authCredentials: {{
                    username: "{user}",
                    password: "{pwd}"
                }}
            }};
        }},
        {{urls: ["<all_urls>"]}},
        ['blocking']
    );
    """

    pluginfile = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", str(manifest_json).replace("'", '"'))
        zp.writestr("background.js", background_js)

    return os.path.abspath(pluginfile)

def watch_video(video_url, proxy=None):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--mute-audio")

    if proxy:
        if "@" in proxy:
            user_pass, ip_port = proxy.split("@")
            plugin_path = create_proxy_extension(ip_port, user_pass)
            options.add_argument(f"--load-extension={plugin_path}")
        else:
            options.add_argument(f"--proxy-server=http://{proxy}")

    driver = uc.Chrome(options=options)

    try:
        driver.get(video_url)
        print("⏳ Sayfa yükleniyor...")

        wait = WebDriverWait(driver, 10)
        video_player = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'video')))

        driver.execute_script("arguments[0].muted = true;", video_player)
        driver.execute_script("arguments[0].play();", video_player)
        print("✅ Video oynatıldı.")

        duration = random.randint(25, 40)
        print(f"🕒 {duration} saniye izleniyor...")
        time.sleep(duration)

    except Exception as e:
        print(f"⚠️ Proxy başarısız veya video bulunamadı: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
        del driver
        print("✅ Tarayıcı kapatıldı.\n")

def load_proxies(filepath):
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    proxies = load_proxies("proxy_list.txt")

    for i, proxy in enumerate(proxies):
        print(f"\n▶️ {i+1}. proxy kullanılıyor: {proxy}")
        watch_video(VIDEO_URL, proxy=proxy)

        if i < len(proxies) - 1:
            delay = random.randint(10, 20)
            print(f"⏱ {delay} saniye bekleniyor...\n")
            time.sleep(delay)

    print("🎉 Tüm proxy izlemeleri tamamlandı.")
