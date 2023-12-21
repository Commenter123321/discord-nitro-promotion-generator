"""
Discord promotion link generator program.
"""

from requests import HTTPError
from random import choice
import concurrent.futures
from time import sleep
import requests
import hashlib
import random
import os

if os.path.exists(".env"):
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=".env")
else:
    print(".env doesn't exist")
    import sys

    sys.exit(1)

PROMOTION_PREFIX = "https://discord.com/billing/partner-promotions/1180231712274387115/"
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY")) or 1.5


def generate_uuid():
    """
    :return: A random Opera GX style UUID or whatever.
    """
    def replace(c):
        num = random.randint(0, 15)
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
    from time import time
    os.makedirs("outputs", exist_ok=True)
    outputFile = f"outputs/output-{str(int(time()))}.txt"
    with open(outputFile, "w+") as f:
        f.write("")
else:
    webhookProxy = os.getenv("PROXY_WEBHOOK")


def save_promotion(promotion_link):
    if not webhookUrl:
        with open(outputFile, "a") as out:
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


s = requests.session()


def worker(n):
    print("worker:", n)
    while True:
        s.cookies.clear()
        r = s.post(
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
            proxies={"https": random.choice(proxies)} if proxies else None,
            timeout=10
        )

        try:
            r.raise_for_status()
        except HTTPError as e:
            print(e)
            continue

        promotion_url = PROMOTION_PREFIX + r.json()["token"]
        print(f"{str(n)}: new promotion:", promotion_url)
        if not save_promotion(promotion_url):
            print("WARNING: couldn't save the promotion url")
        sleep(REQUEST_DELAY)


THREAD_AMOUNT = int(os.getenv("THREAD_AMOUNT")) or 3

with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_AMOUNT) as executor:
    for i in range(THREAD_AMOUNT):
        executor.submit(worker, i)
