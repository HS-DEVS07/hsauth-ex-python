"""
Official HS DEVS AUTH Python Client SDK
Zero external dependencies required (Uses Python standard library).
Compatible with Python 3.7+
"""

import sys
import os
import json
import time
import hashlib
import platform
import subprocess
import threading
import urllib.request
import urllib.parse
import urllib.error

class api:
    def __init__(self, name, ownerid, version="1.0", api_url="https://hsauth.mujahid.xyz/api/1.3/"):
        self.name = name
        self.ownerid = ownerid
        self.version = version
        self.api_url = api_url.rstrip("/") + "/"
        self.sessionid = ""
        self.initialized = False
        self.user_data = {}
        self.app_data = {}
        self.response = {"success": False, "message": ""}
        self.heartbeat_running = False
        self.heartbeat_thread = None
        self.on_message_callback = None

    def _get_hwid(self):
        try:
            if platform.system() == "Windows":
                # Try Windows Registry MachineGuid
                cmd = 'powershell -Command "(Get-ItemProperty -Path Registry::HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography).MachineGuid"'
                guid = subprocess.check_output(cmd, shell=True).decode().strip()
                if guid:
                    return guid
            elif platform.system() == "Linux":
                if os.path.exists("/etc/machine-id"):
                    with open("/etc/machine-id") as f:
                        return f.read().strip()
            elif platform.system() == "Darwin":
                cmd = "ioreg -rd1 -c IOPlatformExpertDevice | awk '/IOPlatformUUID/ { split($0, line, \"\\\"\"); print line[4] }'"
                uuid = subprocess.check_output(cmd, shell=True).decode().strip()
                if uuid:
                    return uuid
        except Exception:
            pass

        # Cross-platform deterministic fallback
        raw = platform.node() + platform.machine() + platform.processor()
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def _req(self, data):
        data["name"] = self.name
        data["ownerid"] = self.ownerid
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(
            self.api_url,
            data=encoded_data,
            headers={"User-Agent": "HSAuth-Python/1.0", "Content-Type": "application/x-www-form-urlencoded"}
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                body = res.read().decode("utf-8")
                try:
                    return json.loads(body)
                except Exception:
                    return {"success": False, "message": body}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                return json.loads(err_body)
            except Exception:
                return {"success": False, "message": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def init(self):
        res = self._req({
            "type": "init",
            "ver": self.version,
            "hash": "python_hash",
        })
        self.response = res
        if res.get("success"):
            self.sessionid = res.get("sessionid", "")
            self.app_data = res.get("appinfo", {})
            self.initialized = True
        elif res.get("message") == "invalidver":
            print(f"[!] New version available! Download: {res.get('download')}")
            sys.exit(1)
        return res

    def _check_init(self):
        if not self.initialized:
            raise RuntimeError("You must call HSAuth.init() before executing authentication methods.")

    def login(self, username, password):
        self._check_init()
        hwid = self._get_hwid()
        res = self._req({
            "type": "login",
            "username": username,
            "pass": password,
            "hwid": hwid,
            "sessionid": self.sessionid,
        })
        self.response = res
        if res.get("success"):
            self.user_data = res.get("info", {})
            self.sessionid = res.get("sessionid", self.sessionid)
            self._handle_active_message(res.get("active_message"))
        return res

    def register(self, username, password, key, email=""):
        self._check_init()
        hwid = self._get_hwid()
        res = self._req({
            "type": "register",
            "username": username,
            "pass": password,
            "key": key,
            "email": email,
            "hwid": hwid,
            "sessionid": self.sessionid,
        })
        self.response = res
        if res.get("success"):
            self.user_data = res.get("info", {})
            self.sessionid = res.get("sessionid", self.sessionid)
            self._handle_active_message(res.get("active_message"))
        return res

    def license(self, key):
        self._check_init()
        hwid = self._get_hwid()
        res = self._req({
            "type": "license",
            "key": key,
            "hwid": hwid,
            "sessionid": self.sessionid,
        })
        self.response = res
        if res.get("success"):
            self.user_data = res.get("info", {})
            self.sessionid = res.get("sessionid", self.sessionid)
            self._handle_active_message(res.get("active_message"))
        return res

    def check(self):
        self._check_init()
        res = self._req({
            "type": "check",
            "sessionid": self.sessionid,
        })
        self.response = res
        if res.get("success"):
            self._handle_active_message(res.get("active_message"))
        return res

    def var(self, varid):
        self._check_init()
        res = self._req({
            "type": "var",
            "varid": varid,
            "sessionid": self.sessionid,
        })
        if res.get("success"):
            return res.get("message") or res.get("response")
        return None

    def getvar(self, varname):
        return self.var(varname)

    def setvar(self, varname, data):
        self._check_init()
        return self._req({
            "type": "setvar",
            "var": varname,
            "data": data,
            "sessionid": self.sessionid,
        })

    def download(self, fileid):
        self._check_init()
        res = self._req({
            "type": "file",
            "fileid": fileid,
            "sessionid": self.sessionid,
        })
        if res.get("success"):
            url = res.get("contents")
            if url and (url.startswith("http://") or url.startswith("https://")):
                with urllib.request.urlopen(url) as f:
                    return f.read()
            return (res.get("contents") or "").encode("utf-8")
        return None

    def log(self, message):
        self._check_init()
        return self._req({
            "type": "log",
            "pcuser": os.getlogin() if hasattr(os, "getlogin") else "user",
            "message": message,
            "sessionid": self.sessionid,
        })

    def fetch_stats(self):
        self._check_init()
        res = self._req({
            "type": "fetchStats",
            "sessionid": self.sessionid,
        })
        if res.get("success") and res.get("appinfo"):
            self.app_data = res.get("appinfo")
        return res

    def fetch_online(self):
        self._check_init()
        res = self._req({
            "type": "fetchOnline",
            "sessionid": self.sessionid,
        })
        return res.get("users", [])

    def logout(self):
        self._check_init()
        self.stop_heartbeat()
        res = self._req({
            "type": "logout",
            "sessionid": self.sessionid,
        })
        self.sessionid = ""
        return res

    def start_heartbeat(self, interval=30, on_message=None):
        if self.heartbeat_running:
            return
        self.heartbeat_running = True
        self.on_message_callback = on_message

        def _loop():
            while self.heartbeat_running:
                time.sleep(interval)
                if not self.heartbeat_running:
                    break
                try:
                    self.check()
                except Exception:
                    pass

        self.heartbeat_thread = threading.Thread(target=_loop, daemon=True)
        self.heartbeat_thread.start()

    def stop_heartbeat(self):
        self.heartbeat_running = False

    def _handle_active_message(self, msg):
        if msg and msg.get("title"):
            if self.on_message_callback:
                self.on_message_callback(msg)
            else:
                print(f"\n[IN-APP BROADCAST - {msg.get('type', 'ANNOUNCEMENT').upper()}]")
                print(f"Title: {msg.get('title')}")
                print(f"Message: {msg.get('content')}\n")

            if msg.get("type") == "killswitch":
                print("[!] KILLSWITCH ACTIVATED BY DEVELOPER. TERMINATING CLIENT.")
                time.sleep(2)
                sys.exit(0)
