"""
Discord promotion link generator program.
"""
from random import choice, randint
from contextlib import suppress
from time import sleep, time
import concurrent.futures
import hashlib
import os

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=".env")

PROMOTION_PREFIX = "https://discord.com/billing/partner-promotions/1180231712274387115/"
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY")) if os.getenv("REQUEST_DELAY") else 1.5


def generate_uuid():
    """
    :return: A random Opera GX style UUID or whatever.
    """
    def replace(c):
        num = randint(0, 15)
        if c == 'x':
            return hex(num)[2:]  # remove '0x' prefix
        return hex((3 & num) | 8)[2:]  # remove '0x' prefix

    uuid_format = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    return ''.join([replace(c) if c in 'xy' else c for c in uuid_format])


def hash_string(input_string):
    """
    :param input_string: The string to hash.
    :return: SHA256 hash of the input.
    """
    return hashlib.sha256(input_string.encode()).hexdigest()


proxies = os.getenv("PROXY")
if proxies is not None:
    proxies = proxies.split(";")
webhookUrl = os.getenv("WEBHOOK_URL")
if not webhookUrl:
    os.makedirs("outputs", exist_ok=True)
    outputFile = f"outputs/output-{str(int(time()))}.txt"
    with open(outputFile, "w+", encoding="utf-8") as f:
        f.write("")
else:
    webhookProxy = os.getenv("PROXY_WEBHOOK")


def save_promotion(promotion_link):
    """
    :param promotion_link: The promotion url to save.
    """
    with suppress():
        if not webhookUrl:
            with open(outputFile, "a", encoding="utf-8") as out:
                out.write(f"{promotion_link}\n")
        else:
            res = requests.post(
                webhookUrl,
                json={"content": f"<{promotion_link}>"},
                timeout=5,
                proxies={"http": webhookProxy, "https": webhookProxy} if webhookProxy else None,
            )
            res.raise_for_status()
            if res.status_code != 204:
                return False
        return True
    return False


def worker(n):
    """
    Starts a worker that generates a discord nitro promotion code.
    :param n: worker id
    """
    r = None
    with suppress():
        r = requests.post(
            "https://api.discord.gx.games/v1/direct-fulfillment",
            headers={
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "accept-encoding": "gzip, deflate, br",
                "content-type": "application/json",
                "sec-ch-ua": "\"Opera GX\";v=\"105\", "
                             "\"Chromium\";v=\"119\", "
                             "\"Not?A_Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "cross-site",
                "referer": "https://www.opera.com/",
                "origin": "https://www.opera.com",
                "user-agent": "Mozilla/5.0 "
                              "(Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 "
                              "(KHTML, like Gecko) "
                              "Chrome/119.0.0.0 "
                              "Safari/537.36 "
                              "OPR/105.0.0.0"
            },
            json={"partnerUserId": hash_string(generate_uuid())},
            proxies={"https": choice(proxies)} if proxies else None,
            timeout=10
        )

    if not r:
        return

    try:
        r.raise_for_status()
    except HTTPError as e:
        print(e)
        return

    promotion_url = PROMOTION_PREFIX + r.json()["token"]
    print(f"{str(n)}: new promotion:", promotion_url)
    if not save_promotion(promotion_url):
        print("WARNING: couldn't save the promotion url")
    sleep(REQUEST_DELAY)


THREAD_AMOUNT = int(os.getenv("THREAD_AMOUNT")) if os.getenv("THREAD_AMOUNT") else 3

with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_AMOUNT) as executor:
    from requests import HTTPError
    import requests
    while True:
        futures = [executor.submit(worker, i) for i in range(THREAD_AMOUNT)]
        concurrent.futures.wait(futures)
