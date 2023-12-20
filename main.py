from operagxdriver import start_opera_driver
from selenium.webdriver.common.by import By
from time import sleep
import requests
import config

promotion_prefix = "https://discord.com/billing/partner-promotions/1180231712274387115/"

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
            driver.refresh()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("error:", e)

    driver.quit()
    print("driver.quit() called, shutting down")
elif config.mode == "request":
    while True:
        r = requests.post(
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
            json={"partnerUserId": "6ef85751becffb5fe975e363950f574a9c8afd4f09e026844c796a339122ba13"},
            proxies={"http": config.proxy, "https": config.proxy} if config.proxy else None
        )

        promotion_url = promotion_prefix + r.json()["token"]
        print("new promotion:", promotion_url)
        requests.post(config.webhook_url, json={"content": f"<{promotion_url}>"})
        sleep(2)
        pass
else:
    raise Exception(f"Invalid mode: '{config.mode}'.")
