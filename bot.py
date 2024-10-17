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

def parse_and_reconstruct(url_encoded_string):
    parsed_data = urllib.parse.parse_qs(url_encoded_string)
    user_data_encoded = parsed_data.get('user', [None])[0]
    
    if user_data_encoded:
        user_data_json = urllib.parse.unquote(user_data_encoded)
    else:
        user_data_json = None
    
    reconstructed_string = f"user={user_data_json}"
    for key, value in parsed_data.items():
        if key != 'user':
            reconstructed_string += f"&{key}={value[0]}"
    
    return reconstructed_string

def generate_random_hex(length=32):
    return secrets.token_hex(length // 2)

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

# Add all other functions here (getgameinfo, getaccountinfo, collectCoin, etc.)
# Make sure to include all the functions you've defined in your original script

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
                    print_("Refresh Token")
                else:
                    print_(f"{datalogin.get('message')}")

        # Add your main logic here
        # This should include all the operations you want to perform for each account
        # Such as getting account info, collecting coins, checking tasks, etc.

        # Example (you need to implement these functions):
        # account_info = getaccountinfo(token, useragent)
        # if account_info:
        #     print_(f"Account balance: {account_info['balance']}")
        
        # collect_coins_result = collectCoin(token, useragent, 250)
        # if collect_coins_result:
        #     print_(f"Collected coins: {collect_coins_result['amount']}")

        # Implement all other operations here

        delay = random.randint(600, 700)
        print_(f"Account {index} waiting for {delay} seconds")
        time.sleep(delay)

def main():
    queries = load_credentials()
    threads = []

    selector_upgrade = input("Auto Upgrade level y/n  : ").strip().lower()

    for index, query in enumerate(queries):
        thread = threading.Thread(target=account_thread, args=(query, index, selector_upgrade))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
