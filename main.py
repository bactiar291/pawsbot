import json
import requests
import time
import random
import os
import urllib3
from colorama import init, Fore, Style
from tabulate import tabulate
from pyfiglet import figlet_format

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    banner_text = figlet_format("BACTIAR 291", font="slant")
    print(Fore.CYAN + banner_text)

def get_random_color():
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA]
    return random.choice(colors)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Origin': 'https://app.notpx.app',
    'Pragma': 'no-cache',
    'Referer': 'https://app.notpx.app/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Content-Type': 'application/json'
})

def ambilData(data_inisial):
    url = "https://api.paws.community/v1/user/auth"
    data = json.dumps({"data": data_inisial})
    try:
        response = session.post(url, data=data, verify=False)
        if response.status_code in [200, 201]:
            response_json = response.json()
            if response_json.get("success"):
                return response_json
            else:
                print(f"{Fore.RED}Gagal mendapatkan token akses: {response_json}")
        else:
            print(f"{Fore.RED}Gagal mendapatkan token akses. Status kode: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Gagal mendapatkan token akses: {e}")
    return None

def ambilTugas(token, daftar_tugas):
    url = "https://api.paws.community/v1/quests/list"
    session.headers['Authorization'] = f'Bearer {token}'
    try:
        response = session.get(url, verify=False)
        if response.status_code in [200, 201, 204]:
            respons_json = response.json()
            for tugas in respons_json['data']:
                judul_tugas = tugas["title"]
                hadiah = tugas['rewards'][0]['amount']
                status = "Terselesaikan" if tugas["progress"]["current"] == 1 and tugas["progress"]["claimed"] else "Dilewati"
                daftar_tugas.append([judul_tugas, hadiah, status])
                
                if tugas["progress"]["current"] == 0:
                    if mulaiTugas(token, tugas["_id"]):
                        print(get_random_color() + f"Tugas berhasil diselesaikan: {judul_tugas}")
                        klaimTugas(token, tugas["_id"], hadiah)
                    else:
                        print(get_random_color() + f"Tugas dilewati: {judul_tugas}")
                elif tugas["progress"]["current"] == 1 and not tugas["progress"]["claimed"]:
                    klaimTugas(token, tugas["_id"], hadiah)
        else:
            print(f"{Fore.RED}Gagal mengambil data tugas. Status kode: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error mengambil tugas: {e}")

def mulaiTugas(token, id_tugas):
    url = 'https://api.paws.community/v1/quests/completed'
    session.headers['Authorization'] = f'Bearer {token}'
    data = json.dumps({"questId": id_tugas})
    try:
        response = session.post(url, data=data, verify=False)
        return response.status_code in [200, 201, 204]
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error mulai tugas: {e}")
    return False

def klaimTugas(token, id_tugas, hadiah):
    url = 'https://api.paws.community/v1/quests/claim'
    data = json.dumps({"questId": id_tugas})
    session.headers['Authorization'] = f'Bearer {token}'
    try:
        response = session.post(url, data=data, verify=False)
        if response.status_code in [200, 201, 204] and response.json().get("success"):
            print(f"{Fore.GREEN}Klaim hadiah berhasil: {hadiah}")
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error klaim tugas: {e}")

def main():
    clear_terminal()
    display_banner()
    
    print("Pembersihan Tugas PAWS")
    file_kueri = "query.txt"
    flag_tugas = input("Apakah Anda ingin mengklaim tugas? (y/n): ") or 'y'
    jeda_bot = input("Masukkan jeda bot dalam detik antara akun: ") or '1'
    jeda_bot = int(jeda_bot)

    jumlah_akun = 0
    saldo_total = 0
    daftar_tugas = []
    with open(file_kueri, 'r') as file:
        for baris in file:
            data_inisial = baris.strip()
            
            clear_terminal()
            print(get_random_color() + f"Memproses Akun #{jumlah_akun + 1}\n")

            hasil = ambilData(data_inisial)
            if hasil:
                token = hasil["data"][0]
                data_pengguna = hasil.get("data", [None, {}])[1]
                nama_pengguna = data_pengguna.get("userData", {}).get("username", "Tidak Ada Nama Pengguna")
                saldo = data_pengguna.get("gameData", {}).get("balance", 0)
                print(get_random_color() + f"Nama Pengguna: {nama_pengguna}")
                saldo_total += saldo
                
                if flag_tugas.lower() == 'y':
                    ambilTugas(token, daftar_tugas)
                jumlah_akun += 1
            
            time.sleep(jeda_bot)
        
        saldo_total_formatted = f"{saldo_total:,}".replace(",", ".")
        print(get_random_color() + "\nSALDO TOTAL:", saldo_total_formatted)

    headers = ["Judul Tugas", "Hadiah", "Status"]
    print("\n" + get_random_color() + tabulate(daftar_tugas, headers, tablefmt="fancy_grid", stralign="center", numalign="center"))

if __name__ == "__main__": 
    main()
