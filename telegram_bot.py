#!/usr/bin/env python3
"""FOMO Insider Telegram bridge. Messaging test only; no live FOMO data or trading."""
import json, os, time, urllib.parse, urllib.request, urllib.error

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
OWNER_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
BASE = f"https://api.telegram.org/bot{TOKEN}"

def api(method, payload=None, timeout=40):
    data = urllib.parse.urlencode(payload or {}).encode()
    req = urllib.request.Request(f"{BASE}/{method}", data=data)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        result = json.loads(response.read().decode())
    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")
    return result["result"]

def send(chat_id, text):
    api("sendMessage", {"chat_id": str(chat_id), "text": text})

def handle(message):
    chat_id = str(message.get("chat", {}).get("id", ""))
    text = (message.get("text") or "").strip()
    if chat_id != OWNER_CHAT_ID:
        return
    if text.startswith("/start"):
        send(chat_id, "FOMO Insider Telegram connection works.\n\nUse /status or /help.\nLive trader data is not connected yet; no trades are placed.")
    elif text.startswith("/status"):
        send(chat_id, "Telegram bridge: ONLINE\nLive FOMO trader feed: NOT CONNECTED\nCSV wallet ranking tool: separate utility\nAuto-trading: DISABLED")
    elif text.startswith("/help"):
        send(chat_id, "Commands:\n/start — connection test\n/status — setup status\n/help — commands")
    else:
        send(chat_id, "Message received. Send /help for commands.")

def main():
    if not TOKEN or not OWNER_CHAT_ID:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in Render Environment.")
    me = api("getMe")
    print("Telegram bridge running as @" + me.get("username", "unknown"), flush=True)
    send(OWNER_CHAT_ID, "FOMO Insider bridge deployed. Telegram connection test successful. Live trader data is not connected yet.")
    offset = None
    while True:
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset
            updates = api("getUpdates", params, timeout=40)
            for update in updates:
                offset = update["update_id"] + 1
                if update.get("message"):
                    try:
                        handle(update["message"])
                    except Exception as exc:
                        print("Message error:", exc, flush=True)
        except urllib.error.HTTPError as exc:
            print("Telegram HTTP error:", exc, flush=True)
            time.sleep(5)
        except Exception as exc:
            print("Polling error:", exc, flush=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
