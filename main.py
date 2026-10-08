#!/usr/bin/env python3
"""
HS DEVS AUTH - Python CLI Example
"""

import sys
import time
from hsauth import api

# Replace with your app credentials from https://hsauth.mujahid.xyz/dashboard
HSAuthApp = api(
    name="MyApp",
    ownerid="your_app_identifier_here",
    version="1.0",
    api_url="https://hsauth.mujahid.xyz/api/1.3/"
)

def broadcast_handler(msg):
    print("\n" + "="*50)
    print(f"[*] LIVE IN-APP BROADCAST: {msg.get('title')}")
    print(f"    Content: {msg.get('content')}")
    print("="*50 + "\n")
    if msg.get("type") == "killswitch":
        print("[!] Killswitch received! Exiting immediately.")
        sys.exit(0)

def main():
    print("""
  _    _  _____         _    _ _______ _    _ 
 | |  | |/ ____|  /\   | |  | |__   __| |  | |
 | |__| | (___   /  \  | |  | |  | |  | |__| |
 |  __  |\___ \ / /\ \ | |  | |  | |  |  __  |
 | |  | |____) / ____ \| |__| |  | |  | |  | |
 |_|  |_|_____/_/    \_\\____/   |_|  |_|  |_|
               Python SDK Client
    """)
    print("[*] Connecting to HS DEVS AUTH server...")
    res = HSAuthApp.init()
    if not res.get("success"):
        print(f"[!] Init Failed: {res.get('message')}")
        return

    print(f"[+] Initialized! App Version: {HSAuthApp.app_data.get('version')}")

    authenticated = False
    while not authenticated:
        print("\n[1] Login with Username & Password")
        print("[2] Register with License Key")
        print("[3] Authenticate with License Key Only")
        print("[4] Exit")
        choice = input("\nSelect option [1-4]: ").strip()

        if choice == "1":
            user = input("Username: ")
            passwd = input("Password: ")
            auth_res = HSAuthApp.login(user, passwd)
        elif choice == "2":
            user = input("Desired Username: ")
            passwd = input("Password: ")
            lic = input("License Key: ")
            auth_res = HSAuthApp.register(user, passwd, lic)
        elif choice == "3":
            lic = input("Enter License Key: ")
            auth_res = HSAuthApp.license(lic)
        elif choice == "4":
            return
        else:
            print("Invalid option.")
            continue

        if auth_res.get("success"):
            authenticated = True
            print(f"\n[+] Success: {auth_res.get('message')}")
        else:
            print(f"\n[!] Failed: {auth_res.get('message')}")

    # Display authenticated profile
    print("\n" + "="*30 + " USER PROFILE " + "="*30)
    print(f"Username: {HSAuthApp.user_data.get('username')}")
    print(f"IP:       {HSAuthApp.user_data.get('ip')}")
    print(f"HWID:     {HSAuthApp.user_data.get('hwid')}")
    print("="*74)

    # Start background heartbeat to receive broadcasts/killswitch
    HSAuthApp.start_heartbeat(interval=30, on_message=broadcast_handler)
    HSAuthApp.log(f"User {HSAuthApp.user_data.get('username')} authenticated via Python client.")

    # Action menu
    while True:
        print("\n--- Features Menu ---")
        print("[1] Read Remote Variable")
        print("[2] Download Protected File")
        print("[3] View Online Users Count")
        print("[4] Send Diagnostic Log")
        print("[5] Logout & Exit")
        act = input("\nSelect action [1-5]: ").strip()

        if act == "1":
            vname = input("Enter Variable Name/ID: ")
            vval = HSAuthApp.var(vname)
            print(f"Value: {vval}")
        elif act == "2":
            fid = input("Enter File Name/ID: ")
            data = HSAuthApp.download(fid)
            if data:
                print(f"[+] Downloaded {len(data)} bytes!")
            else:
                print("[!] Download failed.")
        elif act == "3":
            online = HSAuthApp.fetch_online()
            print(f"[+] Online Users: {len(online)}")
        elif act == "4":
            msg = input("Log Message: ")
            HSAuthApp.log(msg)
            print("[+] Log sent!")
        elif act == "5":
            HSAuthApp.logout()
            print("Logged out. Goodbye!")
            break

if __name__ == "__main__":
    main()
