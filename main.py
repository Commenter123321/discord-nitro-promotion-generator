from operagxdriver import start_opera_driver
from selenium.webdriver.common.by import By
from time import sleep
import requests
import hashlib
import config
import random

promotion_prefix = "https://discord.com/billing/partner-promotions/1180231712274387115/"


def generate_uuid():
    def replace(c):
        r = random.randint(0, 15)
        if c == 'x':
            return hex(r)[2:]  # remove '0x' prefix
        else:
            return hex((3 & r) | 8)[2:]  # remove '0x' prefix

    uuid_format = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    return ''.join([replace(c) if c in 'xy' else c for c in uuid_format])


def hash_string(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()


if config.mode == "webdriver":
    driver = start_opera_driver(
        opera_browser_exe=config.opera_gx_executable,
        opera_driver_exe=config.opera_driver,
        arguments=(
            "--no-sandbox",
            "--test-type",
            "--no-default-browser-check",
            "--no-first-run",
            "--incognito",
            "--start-maximized",
            f"--proxy-server={config.proxy}",
        ) if config.proxy else (
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
                try:
                    claim_btn = driver.find_element(By.XPATH, "//span[@id='claim-button']")
                    if claim_btn is not None:
                        claim_btn.click()
                        break
                except:
                    sleep(2)
                    continue


        def find_promo_link():
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                if "https://discord.com" in driver.current_url:
                    print("new promotion:", driver.current_url)
                    requests.post(config.webhook_url, json={"content": f"<{driver.current_url}>"})
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
elif config.mode == "request":
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
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0"
            },
            json={"partnerUserId": hash_string(generate_uuid())},
            proxies={"http": config.proxy, "https": config.proxy} if config.proxy else None
        )

        promotion_url = promotion_prefix + r.json()["token"]
        print("new promotion:", promotion_url)
        requests.post(config.webhook_url, json={"content": f"<{promotion_url}>"})
        sleep(config.request_delay)
        pass
else:
    raise Exception(f"Invalid mode: '{config.mode}'.")
