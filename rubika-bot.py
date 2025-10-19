# -*- coding: utf-8 -*-
# Rubika Bot — Polling optimized:
# - requests.Session() (keep-alive)
# - json=payload (بدون dumps دستی)
# - sleep پویا (۰.۲ تا ۰.۸ ثانیه)
# - limit کوچک
import os, json, time, requests
from typing import Optional, Dict, Any

TOKEN = "EABBE0EKDIDVJFQEPLBKVCXCMDFCWMFIBMQPYCNUUNLAGXFHZYYUIDABSNKCFQZN"
BASE  = f"https://botapi.rubika.ir/v3/{TOKEN}"
OFFSET_FILE = "rubika_offset.json"
SKIP_BACKLOG_ON_FIRST_RUN = True

# ---- Your data ----
OFFICE_TEXT   = "خیابان آزادی ما بین تقاطع طالقانی و آخر شهناز ساختمان شایان طبقه اول واحد ۳"
COMPANY_TEXT  = "اتوبان تبریز صوفیان شهرک صنعتی بعثت خیابان باکری فلکه دوم"
OFFICE_MAP    = "https://maps.app.goo.gl/kXc4K7hBZGewdyui9?g_st=atm"
COMPANY_MAP   = "https://maps.app.goo.gl/aKtHxwHchhpnAunL8?g_st=atm"
MOBILE        = "۰۹۱۴۹۹۴۹۹۴۹"
LANDLINE      = "۳۵۴۱۹۹۹۹-۰۴۱"
URL_HOME      = "https://esgat.ir/"
URL_SCRAP     = "https://esgat.ir/register"
URL_PRICE     = "https://esgat.ir/inquiry"
URL_FEEDBACK  = "https://esgat.ir/contact-us"
URL_NEWS      = "https://esgat.ir/news"
URL_INSTAGRAM = "https://instagram.com/dorkar_farshbaf"
URL_TELEGRAM  = "https://t.me/dorkar1126"

# ---- Session (keep-alive) ----
session = requests.Session()
session.headers.update({"Content-Type": "application/json"})

def api(method: str, payload: Optional[dict] = None, timeout=12) -> tuple[int, Dict[str, Any]]:
    if payload is None: payload = {}
    r = session.post(f"{BASE}/{method}", json=payload, timeout=timeout)
    if r.headers.get("Content-Type","").startswith("application/json"):
        return r.status_code, r.json()
    return r.status_code, {}

def load_offset() -> Optional[str]:
    if not os.path.exists(OFFSET_FILE): return None
    try:
        with open(OFFSET_FILE, "r", encoding="utf-8") as f:
            return (json.load(f) or {}).get("next_offset_id")
    except: return None

def save_offset(offset: Optional[str]):
    if not offset: return
    with open(OFFSET_FILE, "w", encoding="utf-8") as f:
        json.dump({"next_offset_id": offset}, f, ensure_ascii=False)

# ---- Keypads (Chat Keypad) ----
def btn(id_, text): return {"id": id_, "type": "Simple", "button_text": text}
def row(*bs):      return {"buttons": list(bs)}
def kb(*rows):     return {"rows": list(rows)}

def kb_main():
    return kb(
        row(btn("address","📍 آدرس"), btn("phone","📞 شماره تماس")),
        row(btn("website","🌐 سایت ما"), btn("social","💬 فضای مجازی")),
    )

def kb_address():
    return kb(
        row(btn("address_office","🏢 آدرس دفتر"), btn("address_company","🏭 آدرس شرکت")),
        row(btn("back_main","⬅️ بازگشت")),
    )

def kb_address_office():
    return kb(
        row(btn("office_text","📝 آدرس متنی"), btn("office_map","🗺 لوکیشن گوگل‌مپ")),
        row(btn("back_address","⬅️ بازگشت")),
    )

def kb_address_company():
    return kb(
        row(btn("company_text","📝 آدرس متنی"), btn("company_map","🗺 لوکیشن گوگل‌مپ")),
        row(btn("back_address","⬅️ بازگشت")),
    )

def kb_phone():
    return kb(
        row(btn("phone_mobile","📱 تلفن همراه"), btn("phone_landline","☎️ تلفن ثابت")),
        row(btn("back_main","⬅️ بازگشت")),
    )

def kb_website():
    return kb(
        row(btn("web_home","🏠 صفحه اصلی"), btn("web_scrap","🚗 ثبت نام خودرو فرسوده")),
        row(btn("web_price","💸 استعلام آنلاین قیمت"), btn("web_feedback","🗣 انتقاد یا پیشنهاد")),
        row(btn("web_news","📰 اخبار")),
        row(btn("back_main","⬅️ بازگشت")),
    )

def kb_social():
    return kb(
        row(btn("social_instagram","📷 اینستاگرام"), btn("social_telegram","📨 تلگرام")),
        row(btn("back_main","⬅️ بازگشت")),
    )

# ---- send helpers ----
def send_text(chat_id: str, text: str):
    api("sendMessage", {"chat_id": chat_id, "text": text})

def send_chat_kb(chat_id: str, text: str, keypad: dict):
    api("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "chat_keypad_type": "New",
        "chat_keypad": keypad
    })

# ---- handlers ----
def handle_start(chat_id: str):
    send_chat_kb(chat_id, "سلام! به ربات شرکت درکار تاوریژ آذربایجان خوش آمدید لطفا یکی از گزینه‌ها را انتخاب کنید:",
                 kb_main())


def handle_button(chat_id: str, btn_id: str):
    if btn_id == "address":
        send_chat_kb(chat_id, "نوع آدرس را انتخاب کنید:", kb_address())
    elif btn_id == "address_office":
        send_chat_kb(chat_id, "آدرس دفتر — یکی را انتخاب کنید:", kb_address_office())
    elif btn_id == "office_text":
        send_text(chat_id, f"📝 آدرس دفتر:\n{OFFICE_TEXT}")
    elif btn_id == "office_map":
        send_text(chat_id, f"🗺 لوکیشن دفتر:\n{OFFICE_MAP}")

    elif btn_id == "address_company":
        send_chat_kb(chat_id, "آدرس شرکت — یکی را انتخاب کنید:", kb_address_company())
    elif btn_id == "company_text":
        send_text(chat_id, f"📝 آدرس شرکت:\n{COMPANY_TEXT}")
    elif btn_id == "company_map":
        send_text(chat_id, f"🗺 لوکیشن شرکت:\n{COMPANY_MAP}")

    elif btn_id == "phone":
        send_chat_kb(chat_id, "نوع شماره تماس را انتخاب کنید:", kb_phone())
    elif btn_id == "phone_mobile":
        send_text(chat_id, f"📱 تلفن همراه: {MOBILE}")
    elif btn_id == "phone_landline":
        send_text(chat_id, f"☎️ تلفن ثابت: {LANDLINE}")

    elif btn_id == "website":
        send_chat_kb(chat_id, "«سایت ما» — یک گزینه را انتخاب کنید:", kb_website())
    elif btn_id == "web_home":
        send_text(chat_id, f"🏠 صفحه اصلی:\n{URL_HOME}")
    elif btn_id == "web_scrap":
        send_text(chat_id, f"🚗 ثبت نام خودرو فرسوده:\n{URL_SCRAP}")
    elif btn_id == "web_price":
        send_text(chat_id, f"💸 استعلام آنلاین قیمت:\n{URL_PRICE}")
    elif btn_id == "web_feedback":
        send_text(chat_id, f"🗣 انتقاد یا پیشنهاد:\n{URL_FEEDBACK}")
    elif btn_id == "web_news":
        send_text(chat_id, f"📰 اخبار:\n{URL_NEWS}")

    elif btn_id == "social":
        send_chat_kb(chat_id, "«فضای مجازی» — یک گزینه را انتخاب کنید:", kb_social())
    elif btn_id == "social_instagram":
        send_text(chat_id, f"📷 اینستاگرام:\n{URL_INSTAGRAM}")
    elif btn_id == "social_telegram":
        send_text(chat_id, f"📨 تلگرام:\n{URL_TELEGRAM}")

    elif btn_id == "back_main":
        send_chat_kb(chat_id, "به منوی اصلی برگشتیم:", kb_main())
    elif btn_id == "back_address":
        send_chat_kb(chat_id, "لطفاً نوع آدرس را انتخاب کنید:", kb_address())

# ---- polling loop (optimized) ----
def run():
    print("⚡️ Fast polling bot is running…")
    api("getMe")

    # skip backlog on first run
    offset = None
    if SKIP_BACKLOG_ON_FIRST_RUN and not os.path.exists(OFFSET_FILE):
        st, data = api("getUpdates", {"limit": 1})
        body = data.get("data", {}) if isinstance(data, dict) else {}
        offset = body.get("next_offset_id")
        if offset:
            with open(OFFSET_FILE, "w", encoding="utf-8") as f:
                json.dump({"next_offset_id": offset}, f, ensure_ascii=False)
        print("⏭️  Backlog skipped. Start from:", offset)
    else:
        # resume from last saved offset
        try:
            with open(OFFSET_FILE, "r", encoding="utf-8") as f:
                offset = (json.load(f) or {}).get("next_offset_id")
        except:
            offset = None

    # dynamic sleep
    idle_sleep = 0.5   # when no update
    hot_sleep  = 0.2   # when updates exist

    while True:
        st, data = api("getUpdates", {"limit": 10, "offset_id": offset})
        body = data.get("data", {}) if isinstance(data, dict) else {}
        updates = body.get("updates", []) or []
        nxt = body.get("next_offset_id") or offset
        if nxt and nxt != offset:
            with open(OFFSET_FILE, "w", encoding="utf-8") as f:
                json.dump({"next_offset_id": nxt}, f, ensure_ascii=False)
            offset = nxt

        had_activity = False

        # only latest /start per chat in this batch
        latest_start: dict[str, dict] = {}

        for u in updates:
            had_activity = True
            t = u.get("type"); chat_id = u.get("chat_id")

            if t == "NewMessage" and chat_id:
                nm = u.get("new_message") or {}
                txt = (nm.get("text") or "").strip()
                aux = nm.get("aux_data") or {}
                btn = aux.get("button_id")


                if txt == "/start":
                    latest_start[chat_id] = {"id": nm.get("message_id")}
                elif btn:
                    handle_button(chat_id, btn)

            elif t == "StartedBot" and chat_id:
                latest_start.setdefault(chat_id, {"id": None})

            # legacy inline_message form (rare)
            im = u.get("inline_message") or {}
            if im:
                cid = im.get("chat_id") or chat_id
                txt2 = (im.get("text") or "").strip()
                aux2 = im.get("aux_data") or {}
                btn2 = aux2.get("button_id")
                if txt2 == "/start" and cid:
                    latest_start[cid] = {"id": im.get("message_id")}
                elif btn2 and cid:
                    handle_button(cid, btn2)

        for cid in latest_start.keys():
            handle_start(cid)

        time.sleep(hot_sleep if had_activity else idle_sleep)

if __name__ == "__main__":
    run()



