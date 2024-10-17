import random
import requests
import time
import urllib.parse
import json
import base64
import socket
from datetime import datetime
import secrets
from urllib.parse import parse_qs, unquote
import threading
import queue

def print_(word):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"[{now}] {word}")

def load_credentials():
    try:
        with open('query_id.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File query_id.txt not found.")
        return []
    except Exception as e:
        print("Error loading credentials:", str(e))
        return []

def getuseragent(index):
    try:
        with open('useragent.txt', 'r') as f:
            useragent = [line.strip() for line in f.readlines()]
        if index < len(useragent):
            return useragent[index]
        else:
            return "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
    except FileNotFoundError:
        return 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'
    except Exception as e:
        return 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'

# Include all other helper functions here (parse_and_reconstruct, generate_random_hex, etc.)

def login(query, useragent):
    url = 'https://api-backend.yescoin.gold/user/login'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-ID,en-US;q=0.9,en;q=0.8,id;q=0.7',
        'content-length': '0',
        'priority': 'u=1, i',
        'Origin': 'https://www.yescoin.gold',
        'Referer': 'https://www.yescoin.gold/',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'User-Agent': useragent
    }
    payload = {
        'code': f'{query}'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            print_(f'Login failed with status code: {response.status_code}')
            return None
    except requests.exceptions.RequestException as e:
        print_(f'Error making login request: {e}')
        return None

# Add all other API interaction functions here (getgameinfo, getaccountinfo, collectCoin, etc.)

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def account_thread(query, index, selector_upgrade):
    token = None
    walletaddr = None
    giftbox = 0
    offline = 0

    interval_giftbox = 3600
    interval_offline = 7200

    while True:
        parse = parse_query(query)
        user = parse.get('user')
        currentTime = int(time.time())
        useragent = getuseragent(index)
        user_data = parse_and_reconstruct(query)
        
        if token is None:
            datalogin = login(user_data, useragent)
            if datalogin is not None:
                codelogin = datalogin.get('code')
                if codelogin == 0:
                    data = datalogin.get('data')
                    token = data.get('token')
                    print_(f"Account {index}: Refresh Token")
                else:
                    print_(f"Account {index}: {datalogin.get('message')}")

        # Add your main logic here
        # This should include all the operations you want to perform for each account
        # Such as getting account info, collecting coins, checking tasks, etc.

        # Example (you need to implement these functions):
        # account_info = getaccountinfo(token, useragent)
        # if account_info:
        #     print_(f"Account {index} balance: {account_info['balance']}")
        
        # collect_coins_result = collectCoin(token, useragent, 250)
        # if collect_coins_result:
        #     print_(f"Account {index} collected coins: {collect_coins_result['amount']}")

        # Implement all other operations here

        delay = random.randint(600, 700)
        print_(f"Account {index} waiting for {delay} seconds")
        time.sleep(delay)

def worker(queue, selector_upgrade):
    while True:
        item = queue.get()
        if item is None:
            break
        index, query = item
        account_thread(query, index, selector_upgrade)
        queue.task_done()

def main():
    queries = load_credentials()
    q = queue.Queue()

    selector_upgrade = input("Auto Upgrade level y/n  : ").strip().lower()

    # Create two worker threads
    threads = []
    for _ in range(2):
        t = threading.Thread(target=worker, args=(q, selector_upgrade))
        t.start()
        threads.append(t)

    # Add tasks to the queue
    for index, query in enumerate(queries):
        q.put((index, query))

    # Block until all tasks are done
    q.join()

    # Stop workers
    for _ in range(2):
        q.put(None)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
