from time import sleep
import contextlib
import hashlib
import random
import os

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=".env")
else:
    print(".env doesn't exist")
    exit(1)

promotionPrefix = "https://discord.com/billing/partner-promotions/1180231712274387115/"


def generate_uuid():
    def replace(c):
        num = random.randint(0, 15)
        if c == 'x':
            return hex(num)[2:]  # remove '0x' prefix
        else:
            return hex((3 & num) | 8)[2:]  # remove '0x' prefix

    uuid_format = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    return ''.join([replace(c) if c in 'xy' else c for c in uuid_format])


def hash_string(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()


mode = os.getenv("mode") or "request"
proxy = os.getenv("proxy")
webhookUrl = os.getenv("webhookUrl")

if mode == "webdriver":
    from operagxdriver import start_opera_driver
    from selenium.webdriver.common.by import By
    driver = start_opera_driver(
        opera_browser_exe=os.getenv("operaGxExecutable") or r"C:\Program Files\Opera GX\opera.exe",
        opera_driver_exe=os.getenv("operaGxDriver") or "operadriver.exe",
        arguments=(
            "--no-sandbox",
            "--test-type",
            "--no-default-browser-check",
            "--no-first-run",
            "--incognito",
            "--start-maximized",
            f"--proxy-server={proxy}",
        ) if proxy else (
            "--no-sandbox",
            "--test-type",
            "--no-default-browser-check",
            "--no-first-run",
            "--incognito",
            "--start-maximized",
        )
    )
    try:
        driver.get("https://www.opera.com/gx/discord-nitro")


        def click_claim_btn():
            while True:
                with contextlib.suppress():
                    claim_btn = driver.find_element(By.XPATH, "//span[@id='claim-button']")
                    if claim_btn is not None:
                        claim_btn.click()
                        break
                sleep(2)
                continue


        def find_promo_link():
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                if "https://discord.com" in driver.current_url:
                    print("new promotion:", driver.current_url)
                    requests.post(webhookUrl, json={"content": f"<{driver.current_url}>"})
                    driver.close()


        def find_free_nitro_site():
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                if "gx/discord-nitro" in driver.current_url:
                    return True
            return False


        while True:
            sleep(4)
            click_claim_btn()
            sleep(4)
            find_promo_link()
            if not find_free_nitro_site():
                break
            driver.delete_all_cookies()
            driver.refresh()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("error:", e)

    driver.quit()
    print("driver.quit() called, shutting down")
elif mode == "request":
    import requests
    requestDelay = float(os.getenv("requestDelay")) or 1.5
    s = requests.session()
    while True:
        s.cookies.clear()
        r = s.post(
            "https://api.discord.gx.games/v1/direct-fulfillment",
            headers={
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "accept-encoding": "gzip, deflate, br",
                "content-type": "application/json",
                "sec-ch-ua": "\"Opera GX\";v=\"105\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "referer": "https://www.opera.com/",
                "origin": "https://www.opera.com",
                "user-agent": "Mozilla/5.0 "
                              "(Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0"
            },
            json={"partnerUserId": hash_string(generate_uuid())},
            proxies={"http": proxy, "https": proxy} if proxy else None
        )
        r.raise_for_status()

        promotion_url = promotionPrefix + r.json()["token"]
        print("new promotion:", promotion_url)
        requests.post(webhookUrl, json={"content": f"<{promotion_url}>"})
        sleep(requestDelay)
else:
    print(f"Invalid mode: '{mode}'.")
    exit(1)
