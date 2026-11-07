import requests
import time
import json
import os
import uuid
import threading
import random
import re
import ast
import html as py_html
import pyotp
from collections import Counter 
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
import sys

# Windows consoles (cp1252) crash on emoji prints — wrap stdout early
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        text = " ".join(str(a) for a in args)
        print(text.encode("ascii", "replace").decode("ascii"), **kwargs)

# ==========================================
# Configuration (Token & Owner ID)
# ==========================================
TOKEN = os.environ.get("BOT_TOKEN", "8663470581:AAHix3_GFnfc8xPXpv_0dFYmG656icsQspc")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = 6632393270
BOT_USERNAME = "@ARF_NumberZone_Bot"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "bot_data.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
WITHDRAWALS_FILE = os.path.join(BASE_DIR, "withdrawals.json")
PHPSESSID_FILE = os.path.join(BASE_DIR, "phpsseid.json")
PROCESSED_OTPS_FILE = os.path.join(BASE_DIR, "processed_otps.json")
FLAGS_FILE = os.path.join(BASE_DIR, "flags.txt")
DEFAULT_FLAG_EMOJI_ID = "5780471598922337683"
CR_API_BASE = "http://51.77.216.195/crapi/mait/viewstats"
CR_API_TOKEN = "Q1ZSRkFBUzRDeGxlgWJkiHJyg11DVHh0W5eTSEGGdIFTYpl2RXiUYw"
HADI_API_BASE = "http://147.135.212.197/crapi/had/viewstats"
HADI_API_TOKEN = "Qk9PSEpBUzSGdIFXWFSNhWiRYEKEUmB8anCBVmNhYWtiYGhKhod5ig"
SHARK_API_BASE = "http://139.99.62.188/crapi/sha/viewstats"
SHARK_API_TOKEN = "eodPSHeXbH9qUXFreXZqR3RpbmVeZ2RaYHFsQWpkbIg"
LAMIX_API_BASE = "http://51.77.216.195/crapi/lamix/viewstats"
LAMIX_API_TOKEN = "WG-XWHuWaXJDkXRdiE9Ranp_bVJzbHBXSIRzhUNfYXw="
CR_API_TYPES = frozenset({"cr_mait", "cr_hadi", "cr_shark", "cr_lamix"})

# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5353032893096567467">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5352862640592949843">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "╔═══════════╗\n       📊 NUMBER BOT\n╚═══════════╝\n🚀 Welcome to Number & OTP Service\n━━━━━━━━━━━━\n✅ Choose an option below\nto continue using the bot.\n━━━━━━━━━━━━\n💎 Premium OTP Service", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 
    "search_number": {"text": "╔═══════════╗\n     🔍 <b>SEARCH NUMBER</b>\n╚═══════════╝\n✅ Enter 3 to 9 digits  \nto search for a number.\n━━━━━━━━━━━━━\n📝 Example:\n➥ 880\n➥ 9227373\n━━━━━━━━━━━━━\n🔍 Fast Number Lookup System", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>{{ref_reward}} TK</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖\n《 😒 WITHDRAWAL 》\n➖➖➖➖➖➖➖\n👋 Total Otp: {total_otp}\n➖➖➖➖➖➖➖\n🫂 Total Reffer :{total_ref}\n➖➖➖➖➖➖➖\n📅 BALANCE: {bal}৳\n➖➖➖➖➖➖➖\n🔐 MINIMUM: {min_w} ৳\n➖➖➖➖➖➖➖\nSELECT METHOD:", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []}
}

bot_settings = {
    "admins": [OWNER_ID],
    "panels": [], 
    "fw_groups": [{"chat_id": "-1002713651662", "buttons": []}], 
    "otp_link": "https://t.me/StockOTPZone",
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    "refer_reward": 0.2,
    "cooldown": 10,
    "num_req": 3,
    "num_share": 1, 
    "support_link": "https://t.me/StockNumberV2BoT",
    "w_methods": ["bKash", "Nagad"],
    "w_group": "", 
    
    "fj_on": False,
    "fj_channels": [], 
    "stex_keys": [], 
    "voltx_keys": [],
    "zenex_keys": [],
    "mino_keys": [],
    "zenex_services": {},
    "mino_services": {},
    "zenex_search_countries": [],
    "mino_search_countries": [],
    "search_countries": [],
    "stex_services": {},
    "voltx_services": {},
    "premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5913463998522592692"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"}
    },
    "premium_apps": {
        "FACEBOOK": {"char": "🚫", "id": "5334807341109908955", "name": "Facebook"},
        "WHATSAPP": {"char": "🚫", "id": "5334759662677957452", "name": "WhatsApp"}
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy(),
    "main_keyboard_layout": [
        [
            {"text": "GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "style": "primary", "enabled": True}, 
            {"text": "Search Number", "icon_custom_emoji_id": "5463352748751753567", "style": "primary", "enabled": True}
        ],
        [
            {"text": "TRAFFIC", "icon_custom_emoji_id": "5352877703043258544", "style": "success", "enabled": True}, 
            {"text": "2FA ONLINE", "icon_custom_emoji_id": "5267421176841398765", "style": "primary", "enabled": True}
        ],
        [
            {"text": "Refer", "icon_custom_emoji_id": "5420396762189831222", "style": "success", "enabled": True}, 
            {"text": "WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "style": "danger", "enabled": True}
        ],
        [
            {"text": "SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "style": "primary", "enabled": True}
        ]
    ]
}

# Local Database Setup
users_db = {}
withdrawals_db = {}
number_batches = {}
used_numbers_list = []
stex_assigned_numbers = {} 
voltx_assigned_numbers = {}
zenex_assigned_numbers = {}
mino_assigned_numbers = {}
STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
ZENEX_BASE_URL = "https://api.zenexnetwork.com"
MINO_BASE_URL = "https://minosms.com"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set()
processed_otps_date = None
processed_otps_lock = threading.Lock()
recent_traffic = []
user_banned_cache = {}
phpsseid_db = {"sessions": {}}
flag_emoji_ids = {}

ISO_TO_DIAL = {
    "af": "93", "ax": "358", "al": "355", "dz": "213", "as": "1684", "ad": "376", "ao": "244",
    "ai": "1264", "ag": "1268", "ar": "54", "am": "374", "aw": "297", "au": "61", "at": "43",
    "az": "994", "bs": "1242", "bh": "973", "bd": "880", "bb": "1246", "by": "375", "be": "32",
    "bz": "501", "bj": "229", "bm": "1441", "bt": "975", "bo": "591", "ba": "387", "bw": "267",
    "br": "55", "io": "246", "vg": "1284", "bn": "673", "bg": "359", "bf": "226", "bi": "257",
    "kh": "855", "cm": "237", "ca": "1", "cv": "238", "bq": "599", "ky": "1345", "cf": "236",
    "td": "235", "cl": "56", "cn": "86", "cx": "61", "cc": "61", "co": "57", "km": "269",
    "cg": "242", "cd": "243", "ck": "682", "cr": "506", "ci": "225", "hr": "385", "cu": "53",
    "cw": "599", "cy": "357", "cz": "420", "dk": "45", "dj": "253", "dm": "1767", "do": "1809",
    "ec": "593", "eg": "20", "sv": "503", "gq": "240", "er": "291", "ee": "372", "et": "251",
    "fk": "500", "fo": "298", "fj": "679", "fi": "358", "fr": "33", "gf": "594", "pf": "689",
    "ga": "241", "gm": "220", "ge": "995", "de": "49", "gh": "233", "gi": "350", "gr": "30",
    "gl": "299", "gd": "1473", "gp": "590", "gu": "1671", "gt": "502", "gg": "44", "gn": "224",
    "gw": "245", "gy": "592", "ht": "509", "hn": "504", "hk": "852", "hu": "36", "is": "354",
    "in": "91", "id": "62", "ir": "98", "iq": "964", "ie": "353", "im": "44", "il": "972",
    "it": "39", "jm": "1876", "jp": "81", "je": "44", "jo": "962", "kz": "7", "ke": "254",
    "ki": "686", "kp": "850", "kr": "82", "xk": "383", "kw": "965", "kg": "996", "la": "856",
    "lv": "371", "lb": "961", "ls": "266", "lr": "231", "ly": "218", "li": "423", "lt": "370",
    "lu": "352", "mo": "853", "mk": "389", "mg": "261", "mw": "265", "my": "60", "mv": "960",
    "ml": "223", "mt": "356", "mh": "692", "mq": "596", "mr": "222", "mu": "230", "yt": "262",
    "mx": "52", "fm": "691", "md": "373", "mc": "377", "mn": "976", "me": "382", "ms": "1664",
    "ma": "212", "mz": "258", "mm": "95", "na": "264", "nr": "674", "np": "977", "nl": "31",
    "nc": "687", "nz": "64", "ni": "505", "ne": "227", "ng": "234", "nu": "683", "nf": "672",
    "mp": "1670", "no": "47", "om": "968", "pk": "92", "pw": "680", "ps": "970", "pa": "507",
    "pg": "675", "py": "595", "pe": "51", "ph": "63", "pn": "870", "pl": "48", "pt": "351",
    "pr": "1787", "qa": "974", "re": "262", "ro": "40", "ru": "7", "rw": "250", "bl": "590",
    "sh": "290", "kn": "1869", "lc": "1758", "pm": "508", "vc": "1784", "ws": "685", "sm": "378",
    "st": "239", "sa": "966", "sn": "221", "rs": "381", "sc": "248", "sl": "232", "sg": "65",
    "sx": "1721", "sk": "421", "si": "386", "sb": "677", "so": "252", "za": "27", "ss": "211",
    "es": "34", "lk": "94", "sd": "249", "sr": "597", "sz": "268", "se": "46", "ch": "41",
    "sy": "963", "tw": "886", "tj": "992", "tz": "255", "th": "66", "tl": "670", "tg": "228",
    "tk": "690", "to": "676", "tt": "1868", "tn": "216", "tr": "90", "tm": "993", "tc": "1649",
    "tv": "688", "vi": "1340", "ug": "256", "ua": "380", "ae": "971", "uy": "598", "uz": "998",
    "vu": "678", "va": "39", "ve": "58", "vn": "84", "wf": "681", "eh": "212", "ye": "967",
    "zm": "260", "zw": "263", "us": "1",
}
DIAL_TO_ISO = {dial: iso.upper() for iso, dial in ISO_TO_DIAL.items()}

def iso_to_flag_char(iso):
    iso = str(iso or "").upper()
    if len(iso) != 2 or not iso.isalpha():
        return "🌍"
    return chr(0x1F1E6 + ord(iso[0]) - ord("A")) + chr(0x1F1E6 + ord(iso[1]) - ord("A"))

def load_flag_emojis():
    global flag_emoji_ids
    if not os.path.exists(FLAGS_FILE):
        flag_emoji_ids = {}
        return
    try:
        with open(FLAGS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"FLAG_EMOJIS\s*=\s*(\{.*\})", content, re.DOTALL)
        if not match:
            flag_emoji_ids = {}
            return
        flag_emoji_ids = ast.literal_eval(match.group(1))
        for data in bot_settings.get("premium_flags", {}).values():
            iso = str(data.get("iso", "")).lower()
            if iso in flag_emoji_ids and not data.get("id"):
                data["id"] = flag_emoji_ids[iso]
        safe_print(f"Loaded {len(flag_emoji_ids)} flag emojis from flags.txt")
    except Exception as e:
        safe_print(f"flags.txt load error: {e}")
        flag_emoji_ids = {}

def load_processed_otps():
    global processed_otps, processed_otps_date
    today = datetime.now(timezone(timedelta(hours=6))).strftime("%Y-%m-%d")
    if not os.path.exists(PROCESSED_OTPS_FILE):
        processed_otps = set()
        processed_otps_date = today
        save_processed_otps()
        return
    try:
        raw = open(PROCESSED_OTPS_FILE, "r", encoding="utf-8").read().strip()
        if not raw:
            processed_otps = set()
            processed_otps_date = today
            save_processed_otps()
            safe_print("processed_otps.json was empty — reset to []")
            return
        data = json.loads(raw)
        stored_date = data.get("date", "")
        if stored_date != today:
            processed_otps = set()
            processed_otps_date = today
            save_processed_otps()
            safe_print(f"processed_otps reset (new day: {today})")
            return
        items = data.get("ids", data if isinstance(data, list) else [])
        # Keep only number|otp keys; drop legacy long fingerprints
        cleaned = set()
        for x in items:
            s = str(x)
            if "|" in s and s.count("|") == 1:
                cleaned.add(s)
        processed_otps = cleaned
        processed_otps_date = today
        safe_print(f"Loaded {len(processed_otps)} processed OTP ids for {today}")
    except Exception as e:
        safe_print(f"processed_otps load error: {e} — resetting file")
        processed_otps = set()
        processed_otps_date = today
        save_processed_otps()

def save_processed_otps():
    global processed_otps_date
    try:
        today = datetime.now(timezone(timedelta(hours=6))).strftime("%Y-%m-%d")
        with processed_otps_lock:
            if processed_otps_date is None:
                processed_otps_date = today
            ids = list(processed_otps)
            payload = {
                "ids": ids,
                "date": processed_otps_date,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        with open(PROCESSED_OTPS_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception as e:
        safe_print(f"processed_otps save error: {e}")

def make_otp_unique_id(num, otp, msg_text="", source="", dt=""):
    """Duplicate key format: number|otp (digits-only number)."""
    clean_num = re.sub(r"\D", "", str(num))
    clean_otp = str(otp).strip()
    return f"{clean_num}|{clean_otp}"

def is_otp_duplicate(unique_id):
    with processed_otps_lock:
        return unique_id in processed_otps

def mark_otp_processed(unique_id):
    with processed_otps_lock:
        processed_otps.add(unique_id)
    threading.Thread(target=save_processed_otps, daemon=True).start()

def reset_processed_otps():
    """Clear today's duplicate OTP store (called at midnight)."""
    global processed_otps, processed_otps_date
    today = datetime.now(timezone(timedelta(hours=6))).strftime("%Y-%m-%d")
    with processed_otps_lock:
        processed_otps.clear()
        processed_otps_date = today
    save_processed_otps()
    safe_print(f"processed_otps cleared for new day: {today}")

def load_phpsseid_db():
    global phpsseid_db
    if os.path.exists(PHPSESSID_FILE):
        try:
            with open(PHPSESSID_FILE, "r", encoding="utf-8") as f:
                phpsseid_db = json.load(f)
        except Exception as e:
            print(f"❌ phpsseid.json load error: {e}")
            phpsseid_db = {"sessions": {}}
    if "sessions" not in phpsseid_db:
        phpsseid_db["sessions"] = {}

def save_phpsseid_db():
    phpsseid_db["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(PHPSESSID_FILE, "w", encoding="utf-8") as f:
            json.dump(phpsseid_db, f, indent=4)
    except Exception as e:
        print(f"❌ phpsseid.json save error: {e}")

def curl_url_key(url):
    try:
        parsed = urlparse(url.strip())
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".lower().rstrip("/")
    except:
        pass
    return url.strip().lower().split("?")[0].rstrip("/")

def get_panel_curl_config(p):
    key = p.get("curl_url_key")
    if not key:
        for src in (p.get("msg_link"), p.get("full_api_url"), p.get("api_url")):
            if src:
                key = curl_url_key(src)
                break
    if key:
        return phpsseid_db.get("sessions", {}).get(key)
    return None

def set_panel_curl_config(p, curl_parsed):
    if not curl_parsed or not curl_parsed.get("url"):
        return None, False
    key = curl_url_key(curl_parsed["url"])
    was_replaced = key in phpsseid_db.get("sessions", {})
    existing = phpsseid_db.get("sessions", {}).get(key, {})
    panel_names = list(existing.get("panel_names", []))
    pname = p.get("name")
    if pname and pname not in panel_names:
        panel_names.append(pname)

    phpsseid_db.setdefault("sessions", {})[key] = {
        "url_key": key,
        "panel_name": pname or existing.get("panel_name", key),
        "panel_names": panel_names,
        "url": curl_parsed["url"],
        "headers": curl_parsed.get("headers", {}),
        "cookies": curl_parsed.get("cookies", {}),
        "cookie_string": curl_parsed.get("cookie_string", ""),
        "verify_ssl": curl_parsed.get("verify_ssl", True),
        "method": curl_parsed.get("method", "GET"),
        "phpsessid": curl_parsed.get("cookies", {}).get("PHPSESSID", ""),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    p["curl_url_key"] = key
    p["msg_link"] = curl_parsed["url"]
    p["login_status"] = "✅ Curl Active & Fetching"
    save_phpsseid_db()
    return key, was_replaced

def delete_panel_curl_config(p):
    key = p.get("curl_url_key")
    if not key and p.get("msg_link"):
        key = curl_url_key(p["msg_link"])
    if key and key in phpsseid_db.get("sessions", {}):
        del phpsseid_db["sessions"][key]
        save_phpsseid_db()

def find_panel_by_curl_key(url_key):
    for ep in bot_settings.get("panels", []):
        if ep.get("curl_url_key") == url_key:
            return ep
    return None

def apply_curl_to_panel(p, curl_parsed):
    url_key, was_replaced = set_panel_curl_config(p, curl_parsed)
    for ep in bot_settings.get("panels", []):
        if ep.get("curl_url_key") == url_key:
            ep["login_status"] = "✅ Curl Active & Fetching"
            ep["msg_link"] = curl_parsed["url"]
    save_db()
    return url_key, was_replaced

def auto_panel_name_from_url(url):
    parsed = urlparse(url)
    host = parsed.netloc.replace(".", "_").replace(":", "_")
    path = (parsed.path.rstrip("/").split("/")[-1] or "panel").replace(".", "_")
    base = f"{host}_{path}"[:45]
    existing_names = {p.get("name") for p in bot_settings.get("panels", [])}
    name = base
    n = 2
    while name in existing_names:
        name = f"{base}_{n}"
        n += 1
    return name

def smart_add_or_update_panel(curl_parsed):
    url_key = curl_url_key(curl_parsed["url"])
    existing = find_panel_by_curl_key(url_key)
    if existing:
        _, was_replaced = apply_curl_to_panel(existing, curl_parsed)
        return "updated", existing, was_replaced
    p_data = {
        "name": auto_panel_name_from_url(curl_parsed["url"]),
        "type": "Curl Panel",
        "status": "ON",
        "records": 0,
        "num_col_name": "number", "num_col_idx": 3,
        "msg_col_name": "message", "msg_col_idx": 6,
        "login_status": "⏳ Setting up"
    }
    apply_curl_to_panel(p_data, curl_parsed)
    bot_settings["panels"].append(p_data)
    save_db()
    return "added", p_data, False

def is_cr_api_panel(p):
    if p.get("type") == "CR API":
        return True
    return p.get("api_type") in CR_API_TYPES

def cr_api_label(p):
    api_type = p.get("api_type", "cr_mait")
    if api_type == "cr_hadi":
        return "CR API (HADI)"
    if api_type == "cr_shark":
        return "CR API (SHARK)"
    if api_type == "cr_lamix":
        return "CR API (LAMIX)"
    return "CR API (mait)"

def get_cr_api_defaults(api_type):
    if api_type == "cr_hadi":
        return HADI_API_BASE, bot_settings.get("hadi_api_token") or HADI_API_TOKEN
    if api_type == "cr_shark":
        return SHARK_API_BASE, bot_settings.get("shark_api_token") or SHARK_API_TOKEN
    if api_type == "cr_lamix":
        return LAMIX_API_BASE, bot_settings.get("lamix_api_token") or LAMIX_API_TOKEN
    return CR_API_BASE, bot_settings.get("cr_api_token") or CR_API_TOKEN

def panel_config_text(p):
    if is_cr_api_panel(p):
        api_url, default_tok = get_cr_api_defaults(p.get("api_type", "cr_mait"))
        tok = (p.get("api_token") or default_tok)[:12]
        return (
            f"⚙️ <b>Configure {p['name']}</b>\n\n"
            f"<b>Type:</b> {cr_api_label(p)}\n"
            f"<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n"
            f"<b>Fetch:</b> {p.get('login_status', 'Unknown')}\n"
            f"<b>URL:</b> <code>{p.get('api_url') or api_url}</code>\n"
            f"<b>Token:</b> <code>{tok}...</code>\n"
            f"<b>Records:</b> {p.get('records', 50)}"
        )
    curl_cfg = get_panel_curl_config(p)
    curl_info = ""
    if curl_cfg:
        sess = curl_cfg.get("phpsessid", "")
        url_k = p.get("curl_url_key", curl_cfg.get("url_key", ""))
        curl_info = f"\n<b>URL:</b> <code>{url_k}</code>\n<b>PHPSESSID:</b> <code>{sess[:16]}...</code>"
    return (
        f"⚙️ <b>Configure {p['name']}</b>\n\n"
        f"<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n"
        f"<b>Fetch:</b> {p.get('login_status', 'Unknown')}{curl_info}\n"
        f"<b>Columns:</b> Number={p.get('num_col_idx', 3)} | Message={p.get('msg_col_idx', 6)}"
    )

def normalize_curl_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\^\s*\n", " ", text)
    text = text.replace("^^", "\x00")
    text = text.replace('^"', '"')
    text = text.replace("^&", "&")
    text = re.sub(r"\^%", "%", text)
    text = text.replace("^", "")
    text = text.replace("\x00", "^")
    return " ".join(text.split())

def parse_curl_command(text):
    text = normalize_curl_text(text.strip())
    if not text.lower().startswith("curl"):
        return None

    result = {
        "url": "",
        "method": "GET",
        "headers": {},
        "cookies": {},
        "cookie_string": "",
        "verify_ssl": True
    }

    if "--insecure" in text.lower() or re.search(r'(?:^|\s)-k(?:\s|$)', text):
        result["verify_ssl"] = False

    tokens = []
    current = ""
    in_quote = None
    for ch in text:
        if in_quote:
            if ch == in_quote:
                in_quote = None
            else:
                current += ch
        elif ch in "\"'":
            in_quote = ch
        elif ch == " ":
            if current:
                tokens.append(current)
                current = ""
        else:
            current += ch
    if current:
        tokens.append(current)

    i = 1
    while i < len(tokens):
        t = tokens[i]
        if t in ("-X", "--request") and i + 1 < len(tokens):
            result["method"] = tokens[i + 1].upper()
            i += 2
        elif t in ("-H", "--header") and i + 1 < len(tokens):
            hv = tokens[i + 1]
            if ":" in hv:
                k, v = hv.split(":", 1)
                result["headers"][k.strip()] = v.strip()
            i += 2
        elif t in ("-b", "--cookie") and i + 1 < len(tokens):
            result["cookie_string"] = tokens[i + 1]
            for part in tokens[i + 1].split(";"):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    result["cookies"][k.strip()] = v.strip()
            i += 2
        elif t.startswith("http"):
            result["url"] = t
            i += 1
        elif t in ("--insecure", "-k", "--location", "-L"):
            i += 1
        else:
            i += 1

    return result if result["url"] else None

def refresh_curl_url_dates(url):
    today = datetime.now().strftime("%Y-%m-%d")
    start = f"{today}%2000:00:00"
    end = f"{today}%2023:59:59"
    url = re.sub(r"fdate1=[^&]*", f"fdate1={start}", url, flags=re.I)
    url = re.sub(r"fdate2=[^&]*", f"fdate2={end}", url, flags=re.I)
    return url

def _is_phone_cell(val):
    if val is None:
        return False
    s = str(val).strip()
    if not s or s.lower() == "null":
        return False
    # Footer / totals rows look like: "0.02,0,0,...,100%,0,0,4"
    if "," in s or "%" in s:
        return False
    clean = re.sub(r"\D", "", s)
    if not (8 <= len(clean) <= 18):
        return False
    # Reject values with letters (route names, etc.)
    if re.search(r"[a-zA-Z]", s):
        return False
    return True

def _is_msg_cell(val):
    if val is None:
        return False
    s = str(val).strip()
    if len(s) < 5 or s.lower() == "null":
        return False
    if extract_otp_code(s):
        return True
    low = s.lower()
    return any(k in low for k in ("code", "otp", "pin", "facebook", "whatsapp", "votre", "verification", "confirm"))

def _is_footer_row(row_val):
    if not row_val:
        return True
    first = str(row_val[0]) if row_val[0] is not None else ""
    if "%" in first or ("," in first and first.count(",") >= 3):
        return True
    # Real CDR rows usually start with a datetime
    if re.match(r"\d{4}-\d{2}-\d{2}", first):
        return False
    # If no cell looks like a phone number, skip
    return not any(_is_phone_cell(c) for c in row_val)

def parse_aaData_rows(data_dict, p):
    """
    Expected aaData row layout (1-based cols used in panel config):
      [1]=Date  [2]=Route  [3]=Number  [4]=Service  [5]=null  [6]=Message  ...
    Example:
      ["2026-07-08 07:58:09","Guinea EMO 02","224655034623","Facebook",null,
       "# 465652 est votre code Facebook ...","$",0.005,0]
    Last row is often a totals footer and is skipped.
    """
    results = []
    rows = data_dict.get("aaData", [])
    try:
        n_idx = int(p.get("num_col_idx", 3)) - 1
    except:
        n_idx = 2
    try:
        m_idx = int(p.get("msg_col_idx", 6)) - 1
    except:
        m_idx = 5

    for row_val in rows:
        if not isinstance(row_val, list):
            continue
        if _is_footer_row(row_val):
            continue

        # Preferred configured columns
        num_val = row_val[n_idx] if 0 <= n_idx < len(row_val) else None
        msg_val = row_val[m_idx] if 0 <= m_idx < len(row_val) else None

        # Auto-fallback if configured columns miss (panel layout differs)
        if not _is_phone_cell(num_val):
            for cell in row_val:
                if _is_phone_cell(cell):
                    num_val = cell
                    break
        if not _is_msg_cell(msg_val):
            for cell in row_val:
                if _is_msg_cell(cell):
                    msg_val = cell
                    break

        if num_val is None or msg_val is None:
            continue

        clean_num = re.sub(r"\D", "", str(num_val))
        if not (8 <= len(clean_num) <= 18):
            continue

        msg_str = str(msg_val).strip()
        otp = extract_otp_code(msg_str)
        if otp and len(msg_str) > 4:
            results.append({"number": clean_num, "message": msg_str, "otp": otp})
    return results

def fetch_curl_panel_cdrs(p):
    curl_cfg = get_panel_curl_config(p)
    if not curl_cfg:
        raise Exception("No curl config in phpsseid.json")

    url = refresh_curl_url_dates(curl_cfg.get("url", ""))
    headers = dict(curl_cfg.get("headers", {}))
    cookies = dict(curl_cfg.get("cookies", {}))
    verify = curl_cfg.get("verify_ssl", True)
    method = curl_cfg.get("method", "GET").upper()

    if method == "POST":
        res = requests.post(url, headers=headers, cookies=cookies, timeout=15, verify=verify)
    else:
        res = requests.get(url, headers=headers, cookies=cookies, timeout=15, verify=verify)

    raw = res.text
    if res.status_code != 200:
        raise Exception(f"HTTP {res.status_code}")

    raw_low = raw.lower().strip()
    # Only treat as session expired when response is an HTML login page, not JSON CDR
    if "aadata" not in raw_low and any(x in raw_low for x in ["sign in to your account", "please sign in", "session expired", "<form"]):
        raise Exception("Session expired")

    try:
        data_dict = res.json()
    except Exception:
        raise Exception("Invalid JSON response")

    if "aaData" not in data_dict:
        raise Exception("No aaData in response (session/login?)")

    return parse_aaData_rows(data_dict, p), raw

def fetch_cr_api_cdrs(p=None):
    """
    CR API (mait / HADI / SHARK / LAMIX) — viewstats JSON:
    {status, total, data:[{dt,num,cli,message,payout}, ...]}
    """
    p = p or {}
    api_type = p.get("api_type", "cr_mait")
    base_url, default_token = get_cr_api_defaults(api_type)
    api_url = p.get("api_url") or base_url
    token = p.get("api_token") or default_token
    today = datetime.now().strftime("%Y-%m-%d")
    default_records = 100 if api_type == "cr_lamix" else 50
    records = default_records
    try:
        records = int(p.get("records") or default_records)
    except Exception:
        records = default_records
    records = max(1, min(records, 200))

    params = {
        "token": token,
        "dt1": f"{today} 00:00:00",
        "dt2": f"{today} 23:59:59",
        "records": records,
    }
    res = requests.get(api_url, params=params, timeout=20)
    raw = res.text
    if res.status_code != 200:
        raise Exception(f"HTTP {res.status_code}")
    try:
        data = res.json()
    except Exception:
        raise Exception("Invalid JSON from CR API")

    if data.get("status") == "error":
        msg = str(data.get("msg") or "CR API error")
        if "no record" in msg.lower():
            return [], raw
        raise Exception(msg)

    # success with empty / missing data is normal
    rows = data.get("data")
    if not rows:
        return [], raw

    results = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        num = re.sub(r"\D", "", str(row.get("num") or ""))
        msg = str(row.get("message") or "").strip()
        cli = str(row.get("cli") or "").strip()
        dt = str(row.get("dt") or "").strip()
        if not (8 <= len(num) <= 18) or len(msg) < 3:
            continue
        otp = extract_otp_code(msg)
        if not otp:
            safe_print(f"CR OTP parse miss [{api_type}] num={num} msg={msg[:60]}")
            continue
        results.append({
            "number": num,
            "message": msg,
            "otp": otp,
            "cli": cli,
            "dt": dt,
        })
    return results, raw

def _ensure_cr_style_panel(api_type, name, base_url, token, settings_key, records=50):
    if not token:
        return False
    bot_settings[settings_key] = token
    for p in bot_settings.get("panels", []):
        if p.get("api_type") == api_type:
            p["api_token"] = token
            p["api_url"] = p.get("api_url") or base_url
            if not p.get("records"):
                p["records"] = records
            if p.get("status") != "ON":
                p["status"] = "ON"
            return False
    bot_settings.setdefault("panels", []).append({
        "name": name,
        "type": "CR API",
        "api_type": api_type,
        "api_url": base_url,
        "api_token": token,
        "status": "ON",
        "records": records,
        "login_status": "Ready",
    })
    save_local_db()
    safe_print(f"Added {name} panel")
    return True

def ensure_cr_api_panel():
    """Ensure CR API MAIT panel exists when token is configured."""
    token = bot_settings.get("cr_api_token") or CR_API_TOKEN
    return _ensure_cr_style_panel("cr_mait", "CR API MAIT", CR_API_BASE, token, "cr_api_token")

def ensure_hadi_api_panel():
    """Ensure CR API HADI panel exists when token is configured."""
    token = bot_settings.get("hadi_api_token") or HADI_API_TOKEN
    return _ensure_cr_style_panel("cr_hadi", "CR API HADI", HADI_API_BASE, token, "hadi_api_token")

def ensure_shark_api_panel():
    """Ensure CR API SHARK panel exists when token is configured."""
    token = bot_settings.get("shark_api_token") or SHARK_API_TOKEN
    return _ensure_cr_style_panel("cr_shark", "CR API SHARK", SHARK_API_BASE, token, "shark_api_token")

def ensure_lamix_api_panel():
    """Ensure CR API LAMIX panel exists when token is configured."""
    token = bot_settings.get("lamix_api_token") or LAMIX_API_TOKEN
    return _ensure_cr_style_panel("cr_lamix", "CR API LAMIX", LAMIX_API_BASE, token, "lamix_api_token", records=100)

def fetch_panel_otps(p):
    """Route panel fetch by type: Curl / CR API."""
    if is_cr_api_panel(p):
        return fetch_cr_api_cdrs(p)
    if get_panel_curl_config(p):
        return fetch_curl_panel_cdrs(p)
    raise Exception("No curl/API config")

# Helper Functions to find/move buttons
def find_btn_in_layout(text):
    layout = bot_settings.get("main_keyboard_layout", [])
    for r_idx, row in enumerate(layout):
        for c_idx, btn in enumerate(row):
            if btn["text"] == text:
                return r_idx, c_idx
    return None, None

user_active_sessions = {}

def normalize_fw_groups():
    """Ensure fw_groups entries are dicts with chat_id + buttons (legacy int/str IDs are migrated)."""
    raw = bot_settings.get("fw_groups", [])
    if not isinstance(raw, list):
        raw = []
    normalized = []
    seen = set()
    for item in raw:
        if isinstance(item, dict):
            chat_id = str(item.get("chat_id", "")).strip()
            buttons = item.get("buttons", [])
            if not isinstance(buttons, list):
                buttons = []
        else:
            # Legacy: bare int/str chat id
            chat_id = str(item).strip()
            buttons = []
        if not chat_id or chat_id in seen:
            continue
        seen.add(chat_id)
        normalized.append({"chat_id": chat_id, "buttons": buttons})

    changed = normalized != bot_settings.get("fw_groups")
    bot_settings["fw_groups"] = normalized
    return changed

def get_fw_chat_id(fw):
    if isinstance(fw, dict):
        return str(fw.get("chat_id", "")).strip()
    return str(fw).strip() if fw is not None else ""

def ensure_panels_from_phpsseid():
    """
    If phpsseid.json has sessions but bot panels list is missing them,
    auto-create ON Curl panels so the monitor actually fetches OTP.
    """
    sessions = phpsseid_db.get("sessions", {})
    if not sessions:
        return 0
    existing_keys = {p.get("curl_url_key") for p in bot_settings.get("panels", []) if p.get("curl_url_key")}
    added = 0
    for key, cfg in sessions.items():
        if key in existing_keys:
            # ensure linked panels stay ON when curl exists
            for p in bot_settings.get("panels", []):
                if p.get("curl_url_key") == key:
                    if p.get("status") != "ON":
                        p["status"] = "ON"
                    if not p.get("num_col_idx"):
                        p["num_col_idx"] = 3
                    if not p.get("msg_col_idx"):
                        p["msg_col_idx"] = 6
            continue
        name = cfg.get("panel_name") or auto_panel_name_from_url(cfg.get("url", key))
        # avoid duplicate names
        names = {p.get("name") for p in bot_settings.get("panels", [])}
        base = name
        n = 2
        while name in names:
            name = f"{base}_{n}"
            n += 1
        bot_settings.setdefault("panels", []).append({
            "name": name,
            "type": "Curl Panel",
            "status": "ON",
            "records": 0,
            "num_col_name": "number", "num_col_idx": 3,
            "msg_col_name": "message", "msg_col_idx": 6,
            "curl_url_key": key,
            "msg_link": cfg.get("url", key),
            "login_status": "✅ Synced from phpsseid.json"
        })
        added += 1
    if added:
        save_local_db()
        safe_print(f"✅ Synced {added} panel(s) from phpsseid.json")
    return added

def forward_otp_to_groups(display_msg, otp, num=None):
    """Send OTP to all configured forward groups (flag emoji on copy button)."""
    normalize_fw_groups()
    groups = bot_settings.get("fw_groups", [])
    if not groups:
        safe_print("No fw_groups configured — OTP not forwarded")
        return
    flag_id = get_flag_emoji_id(num) if num else DEFAULT_FLAG_EMOJI_ID
    for fw in groups:
        chat_id = get_fw_chat_id(fw)
        if not chat_id:
            continue
        try:
            kb = {"inline_keyboard": [[
                {
                    "text": str(otp),
                    "icon_custom_emoji_id": flag_id,
                    "copy_text": {"text": str(otp)},
                    "style": "success",
                }
            ]]}
            if isinstance(fw, dict):
                for btn in fw.get("buttons", []):
                    if btn.get("enabled", True):
                        b_obj = {"text": btn["text"], "url": btn["url"], "style": btn.get("style", "primary")}
                        if "icon_custom_emoji_id" in btn:
                            b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                        kb["inline_keyboard"].append([b_obj])
            res = send_message(chat_id, display_msg, reply_markup=kb)
            if res and res.get("ok"):
                safe_print(f"OTP {otp} forwarded to {chat_id}")
            else:
                plain = f"{display_msg}\n\nOTP: <code>{otp}</code>"
                res2 = send_message(chat_id, plain)
                if res2 and res2.get("ok"):
                    safe_print(f"OTP {otp} forwarded (plain) to {chat_id}")
                else:
                    safe_print(f"OTP forward failed to {chat_id}: {res} | fallback={res2}")
        except Exception as e:
            safe_print(f"OTP forward error to {chat_id}: {e}")

def load_db():
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic, users_db, withdrawals_db, stex_assigned_numbers, voltx_assigned_numbers, zenex_assigned_numbers, mino_assigned_numbers
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                saved_settings = data.get("bot_settings", {})
                for key, val in saved_settings.items():
                    if key == "custom_messages":
                        for m_key, m_val in val.items():
                            bot_settings["custom_messages"][m_key] = m_val
                    else:
                        bot_settings[key] = val
                        
                for m_key, m_val in DEFAULT_CUSTOM_MESSAGES.items():
                    if m_key not in bot_settings["custom_messages"]:
                        bot_settings["custom_messages"][m_key] = m_val
                        
                # Handle Database Migrations from Nexa to Stex
                if "nexa_keys" in saved_settings:
                    bot_settings["stex_keys"] = saved_settings["nexa_keys"]
                if "nexa_services" in saved_settings:
                    bot_settings["stex_services"] = saved_settings["nexa_services"]

                number_batches = data.get("number_batches", {})
                used_numbers_list = data.get("used_numbers_list", [])
                total_uploaded_stats = data.get("total_uploaded_stats", 0)
                total_assigned_stats = data.get("total_assigned_stats", 0)
                recent_traffic = data.get("recent_traffic", [])
                stex_assigned_numbers = data.get("stex_assigned_numbers", data.get("nexa_assigned_numbers", {}))
                voltx_assigned_numbers = data.get("voltx_assigned_numbers", {})
                zenex_assigned_numbers = data.get("zenex_assigned_numbers", {})
                mino_assigned_numbers = data.get("mino_assigned_numbers", {})
            print("✅ Database Loaded!")
            avail = sum(len(b.get("numbers", [])) for b in number_batches.values())
            print(f"📦 Local stock: {avail} numbers in {len(number_batches)} batches | Stex services: {len(bot_settings.get('stex_services', {}))} | Voltx: {len(bot_settings.get('voltx_services', {}))}")
            print(f"📁 DB path: {DB_FILE}")
        except Exception as e:
            print(f"❌ Database Load Error: {e}")
    else:
        print(f"⚠️ No bot_data.json found at: {DB_FILE}")
        print("⚠️ Upload numbers from Admin Panel — stock is empty until then.")

    # Migrate legacy fw_groups ints → dict format
    if normalize_fw_groups():
        save_local_db()
        print("✅ Migrated fw_groups to dict format")

    # Load local users & withdrawals
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding='utf-8') as f:
                users_db = json.load(f)
        except: pass

    if os.path.exists(WITHDRAWALS_FILE):
        try:
            with open(WITHDRAWALS_FILE, "r", encoding='utf-8') as f:
                withdrawals_db = json.load(f)
        except: pass

# NOTE: ensure_panels_from_phpsseid is called after load_phpsseid_db() below

def save_local_db():
    local_data = {
        "bot_settings": bot_settings,
        "number_batches": number_batches,
        "used_numbers_list": used_numbers_list,
        "total_uploaded_stats": total_uploaded_stats,
        "total_assigned_stats": total_assigned_stats,
        "recent_traffic": recent_traffic,
        "stex_assigned_numbers": stex_assigned_numbers,
        "voltx_assigned_numbers": voltx_assigned_numbers,
        "zenex_assigned_numbers": zenex_assigned_numbers,
        "mino_assigned_numbers": mino_assigned_numbers
    }
    try:
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump(local_data, f, indent=4)
        with open(USERS_FILE, "w", encoding='utf-8') as f:
            json.dump(users_db, f, indent=4)
        with open(WITHDRAWALS_FILE, "w", encoding='utf-8') as f:
            json.dump(withdrawals_db, f, indent=4)
    except Exception as e:
        print(f"❌ DB Save Error: {e}")

def save_db():
    threading.Thread(target=save_local_db, daemon=True).start()

load_db()
load_flag_emojis()
load_phpsseid_db()
load_processed_otps()
ensure_panels_from_phpsseid()
ensure_cr_api_panel()
ensure_hadi_api_panel()
ensure_shark_api_panel()
ensure_lamix_api_panel()
normalize_fw_groups()
safe_print(f"Panels ready: {len(bot_settings.get('panels', []))} | FW groups: {len(bot_settings.get('fw_groups', []))}")

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}

# ==========================================
# Telegram API & Helpers
# ==========================================
tg_session = requests.Session()

def api_call(method, payload=None, timeout=15):
    # Telegram long-poll waits up to `timeout` seconds with no data — HTTP timeout must be higher
    if method == "getUpdates" and timeout < 60:
        timeout = 60
    url = f"{BASE_URL}/{method}"
    try:
        res = tg_session.post(url, json=payload, timeout=timeout)
        data = res.json()
        if method == "sendMessage" and not data.get("ok"):
            print(f"⚠️ sendMessage failed: {data.get('description')} | chat_id={payload.get('chat_id') if payload else None}")
        return data
    except requests.exceptions.ReadTimeout:
        if method == "getUpdates":
            return {}
        print(f"⚠️ api_call timeout ({method})")
        return {}
    except Exception as e:
        if method == "getUpdates":
            return {}
        print(f"⚠️ api_call error ({method}): {e}")
        return {}

def get_updates(offset=None, timeout=50):
    payload = {"timeout": timeout}
    if offset is not None:
        payload["offset"] = offset
    # HTTP timeout = Telegram long-poll + buffer
    return api_call("getUpdates", payload, timeout=timeout + 10)

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("editMessageText", payload)

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

# Blank bodies tried in order (Telegram rejects some invisible-only texts as "empty")
BLANK_BODIES = ["ㅤ\n", "\u2800", "\u200b\u2800", "·"]

def edit_blank_keyboard(chat_id, message_id, markup, body_text=None):
    """Edit message to body_text (or a blank body) + buttons. Returns last API response."""
    res = {}
    for body in ([body_text] if body_text else []) + BLANK_BODIES:
        res = edit_message(chat_id, message_id, body, reply_markup=markup)
        if res and res.get("ok"):
            return res
        desc = str((res or {}).get("description", ""))
        if "not modified" in desc:
            return {"ok": True}
        safe_print(f"edit_blank_keyboard failed ({desc}) body={body!r}")
    return res

def send_blank_keyboard(chat_id, markup, body_text=None):
    res = {}
    for body in ([body_text] if body_text else []) + BLANK_BODIES:
        res = send_message(chat_id, body, reply_markup=markup)
        if res and res.get("ok"):
            return res
    return res

def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})

def send_document(chat_id, filename, text_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, text_content)}
    data = {'chat_id': chat_id}
    try: requests.post(url, data=data, files=files)
    except: pass

# Local User Sync
all_known_users = set()

def sync_users_list():
    global all_known_users
    try:
        all_known_users = set(users_db.keys())
        if os.path.exists("users_list.json"):
            with open("users_list.json", "r") as f:
                all_known_users.update(json.load(f))
        with open("users_list.json", "w") as f:
            json.dump(list(all_known_users), f)
    except: pass

threading.Thread(target=sync_users_list, daemon=True).start()

def _save_users_list():
    try:
        with open("users_list.json", "w") as f:
            json.dump(list(all_known_users), f)
    except: pass

def register_user_local(uid):
    uid_str = str(uid)
    if uid_str not in all_known_users:
        all_known_users.add(uid_str)
        threading.Thread(target=_save_users_list, daemon=True).start()

def broadcast_copymessage(from_chat_id, msg_id):
    success = 0
    failed = 0
    users = list(all_known_users)
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): success += 1
            else: failed += 1
        except:
            failed += 1
        time.sleep(0.035)
        
    send_message(from_chat_id, render_body_text(f"📢 <b>Broadcast Completed!</b>\n✅ Success: {success}\n❌ Failed: {failed}\n👥 Total Sent: {len(users)}"))

def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)

def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities: return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception as e:
        return text 

def get_flag_info_from_num(num):
    clean = re.sub(r"\D", "", str(num))
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            iso = data.get("iso", "XX")
            eid = data.get("id") or flag_emoji_ids.get(str(iso).lower())
            return data.get("char") or iso_to_flag_char(iso), iso, eid
    sorted_dial = sorted(DIAL_TO_ISO.keys(), key=len, reverse=True)
    for code in sorted_dial:
        if clean.startswith(code):
            iso = DIAL_TO_ISO[code]
            eid = flag_emoji_ids.get(iso.lower())
            return iso_to_flag_char(iso), iso, eid
    return "🌍", "XX", DEFAULT_FLAG_EMOJI_ID

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso

def get_flag_emoji_id(num):
    _, iso, eid = get_flag_info_from_num(num)
    if eid:
        return str(eid)
    flags_db = bot_settings.get("premium_flags", {})
    for flag_data in flags_db.values():
        if iso == flag_data.get("iso") and flag_data.get("id"):
            return str(flag_data["id"])
    if iso and iso != "XX":
        file_id = flag_emoji_ids.get(str(iso).lower())
        if file_id:
            return str(file_id)
    return DEFAULT_FLAG_EMOJI_ID

def get_flag_info_html(num_or_iso):
    if len(num_or_iso) == 2:
        iso = num_or_iso.upper()
        for data in bot_settings.get("premium_flags", {}).values():
            if data.get("iso") == iso:
                eid = data.get("id") or flag_emoji_ids.get(iso.lower())
                char = data.get("char") or iso_to_flag_char(iso)
                if eid:
                    return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        eid = flag_emoji_ids.get(iso.lower())
        if eid:
            char = iso_to_flag_char(iso)
            return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
        return "🌍"
        
    char, _, eid = get_flag_info_from_num(num_or_iso)
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char

COUNTRY_NAMES = {p.split(" ", 1)[0]: p.split(" ", 1)[1] for p in "af Afghanistan|ax Aland Islands|al Albania|dz Algeria|as American Samoa|ad Andorra|ao Angola|ai Anguilla|ag Antigua and Barbuda|ar Argentina|am Armenia|aw Aruba|au Australia|at Austria|az Azerbaijan|bs Bahamas|bh Bahrain|bd Bangladesh|bb Barbados|by Belarus|be Belgium|bz Belize|bj Benin|bm Bermuda|bt Bhutan|bo Bolivia|ba Bosnia and Herzegovina|bw Botswana|br Brazil|io British Indian Ocean Territory|vg British Virgin Islands|bn Brunei|bg Bulgaria|bf Burkina Faso|bi Burundi|kh Cambodia|cm Cameroon|ca Canada|cv Cape Verde|bq Caribbean Netherlands|ky Cayman Islands|cf Central African Republic|td Chad|cl Chile|cn China|cx Christmas Island|cc Cocos Islands|co Colombia|km Comoros|cg Congo|cd DR Congo|ck Cook Islands|cr Costa Rica|ci Ivory Coast|hr Croatia|cu Cuba|cw Curacao|cy Cyprus|cz Czech Republic|dk Denmark|dj Djibouti|dm Dominica|do Dominican Republic|ec Ecuador|eg Egypt|sv El Salvador|gq Equatorial Guinea|er Eritrea|ee Estonia|et Ethiopia|fk Falkland Islands|fo Faroe Islands|fj Fiji|fi Finland|fr France|gf French Guiana|pf French Polynesia|ga Gabon|gm Gambia|ge Georgia|de Germany|gh Ghana|gi Gibraltar|gr Greece|gl Greenland|gd Grenada|gp Guadeloupe|gu Guam|gt Guatemala|gg Guernsey|gn Guinea|gw Guinea-Bissau|gy Guyana|ht Haiti|hn Honduras|hk Hong Kong|hu Hungary|is Iceland|in India|id Indonesia|ir Iran|iq Iraq|ie Ireland|im Isle of Man|il Israel|it Italy|jm Jamaica|jp Japan|je Jersey|jo Jordan|kz Kazakhstan|ke Kenya|ki Kiribati|kp North Korea|kr South Korea|xk Kosovo|kw Kuwait|kg Kyrgyzstan|la Laos|lv Latvia|lb Lebanon|ls Lesotho|lr Liberia|ly Libya|li Liechtenstein|lt Lithuania|lu Luxembourg|mo Macau|mk North Macedonia|mg Madagascar|mw Malawi|my Malaysia|mv Maldives|ml Mali|mt Malta|mh Marshall Islands|mq Martinique|mr Mauritania|mu Mauritius|yt Mayotte|mx Mexico|fm Micronesia|md Moldova|mc Monaco|mn Mongolia|me Montenegro|ms Montserrat|ma Morocco|mz Mozambique|mm Myanmar|na Namibia|nr Nauru|np Nepal|nl Netherlands|nc New Caledonia|nz New Zealand|ni Nicaragua|ne Niger|ng Nigeria|nu Niue|nf Norfolk Island|mp Northern Mariana Islands|no Norway|om Oman|pk Pakistan|pw Palau|ps Palestine|pa Panama|pg Papua New Guinea|py Paraguay|pe Peru|ph Philippines|pn Pitcairn|pl Poland|pt Portugal|pr Puerto Rico|qa Qatar|re Reunion|ro Romania|ru Russia|rw Rwanda|bl Saint Barthelemy|sh Saint Helena|kn Saint Kitts and Nevis|lc Saint Lucia|pm Saint Pierre and Miquelon|vc Saint Vincent|ws Samoa|sm San Marino|st Sao Tome and Principe|sa Saudi Arabia|sn Senegal|rs Serbia|sc Seychelles|sl Sierra Leone|sg Singapore|sx Sint Maarten|sk Slovakia|si Slovenia|sb Solomon Islands|so Somalia|za South Africa|ss South Sudan|es Spain|lk Sri Lanka|sd Sudan|sr Suriname|sz Eswatini|se Sweden|ch Switzerland|sy Syria|tw Taiwan|tj Tajikistan|tz Tanzania|th Thailand|tl Timor-Leste|tg Togo|tk Tokelau|to Tonga|tt Trinidad and Tobago|tn Tunisia|tr Turkey|tm Turkmenistan|tc Turks and Caicos|tv Tuvalu|vi US Virgin Islands|ug Uganda|ua Ukraine|ae United Arab Emirates|gb United Kingdom|uy Uruguay|uz Uzbekistan|vu Vanuatu|va Vatican City|ve Venezuela|vn Vietnam|wf Wallis and Futuna|eh Western Sahara|ye Yemen|zm Zambia|zw Zimbabwe|us United States".split("|")}

def get_country_name(iso):
    iso_u = str(iso or "").upper()
    for data in bot_settings.get("premium_flags", {}).values():
        if str(data.get("iso", "")).upper() == iso_u and data.get("name"):
            return data["name"]
    return COUNTRY_NAMES.get(iso_u.lower(), iso_u or "Unknown")

def build_group_otp_message(num, otp, msg_text, prem_app_html, app_full_name):
    """OTP Received card posted to the OTP group."""
    clean = re.sub(r"\D", "", str(num))
    masked = f"{clean[:2]}{'*' * max(len(clean) - 6, 2)}{clean[-4:]}" if len(clean) > 6 else clean
    char, iso = get_flag_and_code(clean)
    flag_html = get_flag_info_html(f"+{clean}")
    now_str = datetime.now(BD_TZ).strftime("%Y-%m-%d %I:%M %p")
    body = py_html.escape(str(msg_text or "").strip())
    return render_body_text(
        "✨ <b>OTP Received</b> ✨\n\n"
        f"⏰ <b>Time:</b> {now_str}\n"
        f"📞 <b>Number:</b> <code>{masked}</code>\n"
        f"🌐 <b>Country:</b> {flag_html} {py_html.escape(get_country_name(iso))}\n"
        f"🔧 <b>Service:</b> {prem_app_html} {py_html.escape(str(app_full_name))}\n"
        f"🔑 <b>OTP Code:</b> <code>{py_html.escape(str(otp))}</code>\n\n"
        f"{body}"
    )

def build_assigned_text(fetched_nums):
    """Text shown above the number buttons."""
    clean = re.sub(r"\D", "", str((fetched_nums or [""])[0]))
    char, iso = get_flag_and_code(clean)
    cands = [ISO_TO_DIAL.get(str(iso).lower(), "")]
    cands += [c for c, d in bot_settings.get("premium_flags", {}).items() if str(d.get("iso", "")).upper() == str(iso).upper()]
    cands = [c for c in cands if c and clean.startswith(c)]
    dial = max(cands, key=len) if cands else ISO_TO_DIAL.get(str(iso).lower(), "")
    lines = ["✅ NUMBERS ASSIGNED SUCCESSFULLY!", ""]
    if iso and iso != "XX":
        lines.append(f"🌐 {get_country_name(iso)} • +{dial} • {str(iso).upper()}")
        lines.append("")
    try:
        reward = float(bot_settings.get("otp_reward", 0.0) or 0.0)
    except Exception:
        reward = 0.0
    if reward > 0:
        lines.append(f"💰 Reward: ৳{reward:.2f} Per OTP! 🥳")
        lines.append("")
    lines.append("⏳ Waiting for incoming SMS... ⚡️")
    return render_body_text("\n".join(lines))

def mask_number(num):
    clean = num.replace("+", "").replace(" ", "")
    if len(clean) > 6: return f"{clean[:3]}❖SNZ❖{clean[-3:]}"
    elif len(clean) > 2: return f"{clean[:1]}❖SNZ❖{clean[-1:]}"
    return clean

# ==========================================
# Service & Language Keywords
# ==========================================
SERVICE_SMS_KEYWORDS = {
    "whatsapp": ["whatsapp", "wa", "wap", "w/a", "whatsapp business", "wa.me", "wa code", "wh", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "वाٹسएप", "वॉट्सऐप", "व्हाट्सप्प", "হোয়াটসঅ্যাপ", "হোটসঅ্যাপ", "ватсап", "уотсап", "вотсап", "ватс апп", "వాట్సాప్", "వాట్సాప్", "வாட்ஸ்அப்", "வாட்ஸ்அப்", "વોટ્સએપ", "ਵਟਸਐਪ", "ହ୍ଵาଟସ୍ ଆପ୍", "වට්ස්ඇප්", "วอตส์แอปป์", "วอทส์แอพ", "ဝက်စ်أကပ်", "វ៉តសាប់", "វ៉តសាប់", "ワッツアップ", "왓츠앱", "whatsapp的", "whatsapp验证码", "וואטסאপ", "γουάτσαπ", "ዋትስአፕ", "ვოთსაფი", "վոթսափ"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code", "فيسبوك", "فيس بوك"],
    "indrive": ["indrive", "in drive", "in-drive"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code", "انستغرام", "انستقرام"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code", "تيك توك"],
    "snapchat": ["snapchat", "snap", "snap code", "سناب شات"],
    "twitter": ["twitter", "x.com", "x code", "twitter code", "تويتر"],
    "discord": ["discord", "discord code", "ديسكورد"],
    "viber": ["viber", "viber code", "فايبر"],
    "line": ["line", "line code", "line verification", "لاين"],
    "wechat": ["wechat", "we chat", "wechat code", "وي تشات"],
    "signal": ["signal", "signal code", "سيجنال"],
    "linkedin": ["linkedin", "linked in", "لينكد إن"],
    "imo": ["imo", "imo code", "imo verification", "ايمো"],
    "kakaotalk": ["kakao", "kakaotalk", "كاكاو"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],
    "google": ["google", "gmail", "youtube", "g-", "google voice", "جوجل", "غوغل"],
    "microsoft": ["microsoft", "ms", "outlook", "live.com", "hotmail"],
    "apple": ["apple", "icloud", "itunes", "apple id"],
    "yahoo": ["yahoo", "yahoo code", "ymail"],
    "protonmail": ["proton", "protonmail"],
    "binance": ["binance", "bnb", "binances"],
    "coinbase": ["coinbase"],
    "okx": ["okx", "okex"],
    "kucoin": ["kucoin"],
    "bybit": ["bybit"],
    "huobi": ["huobi", "htx"],
    "mexc": ["mexc"],
    "trustwallet": ["trust wallet", "trustwallet"],
    "bkash": ["bkash", "b-kash", "bkash code"],
    "nagad": ["nagad", "nagad code"],
    "rocket": ["rocket", "dutch bangla"],
    "upay": ["upay", "upay code"],
    "paypal": ["paypal", "pay pal"],
    "paytm": ["paytm"],
    "cashapp": ["cash app", "cashapp"],
    "wise": ["wise", "transferwise"],
    "amazon": ["amazon", "amzn", "amazon code"],
    "ebay": ["ebay"],
    "aliexpress": ["aliexpress", "ali express"],
    "alibaba": ["alibaba"],
    "daraz": ["daraz", "daraz code"],
    "foodpanda": ["foodpanda", "food panda"],
    "uber": ["uber", "uber code", "uber verification", "uber eats"],
    "pathao": ["pathao", "pathao ride"],
    "netflix": ["netflix", "netflix code"],
    "spotify": ["spotify", "spotify code"],
    "steam": ["steam", "steam guard"],
    "epicgames": ["epic games", "epicgames"],
    "roblox": ["roblox", "roblox code"],
    "riotgames": ["riot", "riot games", "valorant", "league of legends"],
    "garena": ["garena", "free fire", "freefire"],
    "playstation": ["playstation", "psn"],
    "1xbet": ["1xbet", "1x bet"],
    "melbet": ["melbet", "melbet code"],
    "linebet": ["linebet"],
    "bet365": ["bet365"],
    "megapari": ["megapari"],
    "tinder": ["tinder", "tinder code"],
    "bumble": ["bumble"],
    "badoo": ["badoo"]
}

def detect_service(text):
    text_lower = str(text).lower()
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return service_key.upper()
    return None

def resolve_otp_service(cli_hint, msg_text, panel_name=None):
    """SMS body wins over panel/CLI route name (e.g. Instagram code in message)."""
    detected = detect_service(msg_text)
    if detected:
        return detected
    hint = cli_hint or panel_name or "Panel"
    cli_key = re.sub(r"[^a-z0-9]", "", str(hint).lower())
    if cli_key and cli_key in SERVICE_SMS_KEYWORDS:
        return cli_key.upper()
    return str(hint).upper().strip()

BD_TZ = timezone(timedelta(hours=6))

def get_local_date():
    return datetime.now(BD_TZ).strftime("%Y-%m-%d")

def check_daily_lb_reset():
    today = get_local_date()
    if bot_settings.get("daily_lb_date") == today:
        return
    for uid in users_db:
        users_db[uid]["daily_otps"] = 0
    bot_settings["daily_lb_date"] = today
    reset_processed_otps()
    save_db()

def increment_user_otp_count(user_id):
    check_daily_lb_reset()
    uid_str = str(user_id)
    if uid_str not in users_db:
        return
    users_db[uid_str]["total_otps"] = users_db[uid_str].get("total_otps", 0) + 1
    users_db[uid_str]["daily_otps"] = users_db[uid_str].get("daily_otps", 0) + 1

def daily_lb_reset_thread():
    global processed_otps_date
    while True:
        try:
            check_daily_lb_reset()
            today = get_local_date()
            if processed_otps_date != today:
                reset_processed_otps()
        except Exception as e:
            safe_print(f"Daily leaderboard reset error: {e}")
        time.sleep(60)

def get_service_info_html(service_text, msg_text=""):
    s = str(service_text).upper().strip()
    m = str(msg_text).lower().strip()
    apps = bot_settings.get("premium_apps", {})
    
    detected_from_msg = detect_service(msg_text) if m else None
    if detected_from_msg:
        detected_service = detected_from_msg
    else:
        cli_key = re.sub(r"[^a-z0-9]", "", s.lower())
        if cli_key and cli_key in SERVICE_SMS_KEYWORDS:
            detected_service = cli_key.upper()
        else:
            detected_service = s

    clean_s = re.sub(r'[^\w\s]', '', detected_service).strip()
    
    for app_name, data in apps.items():
        if app_name == detected_service or app_name == clean_s or app_name in detected_service or detected_service in app_name:
            full_name = data.get("name", app_name.title())
            char = data.get("char", "📱")
            eid = data.get("id")
            if eid: return full_name, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            return full_name, char
            
    if len(detected_service) > 20:
        return "Message", "💬"
        
    return detected_service.title(), "📱"

def detect_language(text):
    if not text: return "#EN"
    text_str = str(text)

    if any('\u0600' <= c <= '\u06ff' for c in text_str): return "#AR"
    if any('\u0980' <= c <= '\u09ff' for c in text_str): return "#BN"
    if any('\u0900' <= c <= '\u097f' for c in text_str): return "#HI"
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str): return "#PA"
    if any('\u0a80' <= c <= '\u0aff' for c in text_str): return "#GU"
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str): return "#OR"
    if any('\u0b80' <= c <= '\u0bff' for c in text_str): return "#TA"
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str): return "#TE"
    if any('\u0c80' <= c <= '\u0cff' for c in text_str): return "#KN"
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str): return "#ML"
    if any('\u0d80' <= c <= '\u0dff' for c in text_str): return "#SI"
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str): return "#TH"
    if any('\u0e80' <= c <= '\u0eff' for c in text_str): return "#LO"
    if any('\u0f00' <= c <= '\u0fff' for c in text_str): return "#BO"
    if any('\u1000' <= c <= '\u109f' for c in text_str): return "#MY"
    if any('\u1200' <= c <= '\u137f' for c in text_str): return "#AM"
    if any('\u1780' <= c <= '\u17ff' for c in text_str): return "#KM"
    if any('\u10a0' <= c <= '\u10ff' for c in text_str): return "#KA"
    if any('\u0530' <= c <= '\u058f' for c in text_str): return "#HY"
    if any('\u0590' <= c <= '\u05ff' for c in text_str): return "#HE"
    if any('\u0370' <= c <= '\u03ff' for c in text_str): return "#EL"
    if any('\u0400' <= c <= '\u04ff' for c in text_str): return "#RU"
    if any('\u4e00' <= c <= '\u9fff' for c in text_str): return "#ZH"
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str): return "#JA"
    if any('\uac00' <= c <= '\ud7af' for c in text_str): return "#KO"

    text_lower = text_str.lower()
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]): return "#ID"
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]): return "#MS"
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]): return "#VN"
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]): return "#TL"
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]): return "#ES"
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]): return "#PT"
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR"
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE"
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]): return "#IT"
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]): return "#PL"
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]): return "#TR"
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]): return "#NL"
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]): return "#SV"
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]): return "#DA"
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]): return "#NO"
    if any(w in text_lower for w in ["gahvistuskoodi", "älä jaa"]): return "#FI"
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]): return "#CS"
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]): return "#SK"
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]): return "#HU"
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]): return "#RO"
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]): return "#HR"
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]): return "#BG"
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]): return "#UK"
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]): return "#SW"
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]): return "#AF"
    
    return "#EN"

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

def check_force_join(user_id):
    if not bot_settings.get("fj_on") or not bot_settings.get("fj_channels"):
        return True
    if is_admin(user_id):
        return True
    for ch in bot_settings["fj_channels"]:
        # Short timeout — never block GET NUMBER for 15s per channel
        res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id}, timeout=5)
        if not res.get("ok"):
            # Treat API errors as not joined (fail closed) but don't hang
            return False
        if res["result"]["status"] in ["left", "kicked"]:
            return False
    return True

def send_force_join_msg(chat_id):
    kb = []
    for ch in bot_settings["fj_channels"]:
        url = f"https://t.me/{ch.replace('@', '')}" if str(ch).startswith("@") else str(ch)
        if not str(url).startswith("http"):
            url = f"https://t.me/{str(ch).lstrip('@')}"
        kb.append([{"text": f"Join Channel", "icon_custom_emoji_id": "5789428375261023681", "url": url, "style": "primary"}])
    kb.append([{"text": "Check Joined", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Please join our channels to use the bot!</b>"), reply_markup={"inline_keyboard": kb})

def is_user_banned(user_id):
    if is_admin(user_id): return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 60:
        return user_banned_cache[user_id]['banned']
    
    uid_str = str(user_id)
    banned = False
    if uid_str in users_db:
        banned = users_db[uid_str].get("banned", False)
        
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned

# ==========================================
# OTP Extraction Core
# ==========================================
def extract_otp_code(text):
    """Extract OTP from SMS (EN / FR / AR + Lamix-style Facebook / inDrive messages)."""
    clean_text = str(text or "")
    # Strip bidi / zero-width marks common in Arabic Facebook SMS
    clean_text = re.sub(r'[\u200B-\u200F\u202A-\u202E\u2060\uFEFF\u00A0]', '', clean_text)
    # Arabic-Indic digits → ASCII
    clean_text = clean_text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789'))
    clean_text = clean_text.replace("\n", " ").replace("\r", " ")
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    # "# 544695 is your Facebook code..." / "#74005" (even if glued to next word)
    hash_otp = re.search(r'#\s*(\d{4,8})(?!\d)', clean_text)
    if hash_otp:
        return hash_otp.group(1)

    # Arabic: "88317705 هو رمز ..." / "... رمز 123456"
    ar_otp = re.search(r'(\d{4,8})\s*(?:هو\s*)?رمز', clean_text)
    if ar_otp:
        return ar_otp.group(1)
    ar_otp2 = re.search(r'رمز(?:\s*(?:هو|إعادة|:))?[^\d]{0,20}(\d{4,8})', clean_text)
    if ar_otp2:
        return ar_otp2.group(1)

    # "inDrive code 3264" / "Facebook code 123456" / "your code is 1234"
    app_code = re.search(
        r'(?:code|otp|pin|verification)\s*(?:is|:|-|=)?\s*(\d{4,8})(?!\d)',
        clean_text, re.I
    )
    if app_code:
        return app_code.group(1)

    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:
        return multi_part.group(0).replace(" ", "").replace("-", "")

    # French: "465652 est votre code"
    fr_match = re.search(r'(\d{4,8})\s+est\s+votre\s+code', clean_text, re.I)
    if fr_match:
        return fr_match.group(1)

    otp_keywords = ['code', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit():
        return keyword_match.group(1)

    keyword_match_rev = re.search(
        rf'(\d{{4,8}})\s*(?:is your|is the|is|কোড)',
        clean_text, re.I
    )
    if keyword_match_rev:
        return keyword_match_rev.group(1)

    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match:
        return g_match.group(1)

    # Prefer typical OTP lengths when multiple digit groups exist
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches:
        for pref_len in (6, 5, 4, 8, 7):
            for d in digit_matches:
                if len(d) == pref_len:
                    return d
        return digit_matches[0]

    return None

def panel_monitor_thread():
    global processed_otps, recent_traffic
    safe_print("Panel monitor started")
    while True:
        try:
            if not bot_settings.get("panels") and phpsseid_db.get("sessions"):
                ensure_panels_from_phpsseid()
            ensure_cr_api_panel()
            ensure_hadi_api_panel()
            ensure_shark_api_panel()
            ensure_lamix_api_panel()

            panels = bot_settings.get("panels", [])
            if not panels:
                time.sleep(5)
                continue

            for idx, p in enumerate(panels):
                if p.get("status") != "ON":
                    continue
                is_cr = is_cr_api_panel(p)
                if not is_cr and not get_panel_curl_config(p):
                    p["login_status"] = "No Curl"
                    continue
                try:
                    parsed_data, res_text = fetch_panel_otps(p)
                    p["login_status"] = f"Active ({len(parsed_data)} rows)"
                except Exception as e:
                    p["login_status"] = f"Failed ({str(e)[:40]})"
                    safe_print(f"Panel fetch error [{p.get('name')}]: {e}")
                    continue

                source = p.get("api_type", "cr") if is_cr else "curl"

                for item in parsed_data:
                    try:
                        num = item["number"]
                        otp = item["otp"]
                        msg_text = item["message"]
                        unique_id = make_otp_unique_id(num, otp)

                        if is_otp_duplicate(unique_id):
                            continue
                        mark_otp_processed(unique_id)

                        char, iso = get_flag_and_code(num)
                        app_name = resolve_otp_service(item.get("cli"), msg_text, p.get("name"))
                        app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                        current_time = time.time()

                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        recent_traffic.append({
                            "service": app_full_name,
                            "iso": iso,
                            "flag": char,
                            "number": num,
                            "time": current_time
                        })

                        display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                        masked = mask_number(display_num)
                        lang = detect_language(msg_text)
                        display_msg = build_group_otp_message(display_num, otp, msg_text, prem_app_html, app_full_name)

                        safe_print(f"New OTP {otp} for {num} from {p.get('name')}")
                        forward_otp_to_groups(display_msg, otp, num=display_num)

                        owners = []
                        clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()

                        for uid, session_data in user_active_sessions.items():
                            for act_num in session_data.get("nums", []):
                                act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                    owners.append(uid)
                                    break

                        if not owners:
                            for stex_n, n_owner in stex_assigned_numbers.items():
                                clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                    owners.append(n_owner)

                        for owner_id in list(set(owners)):
                            inbox_msg = render_body_text(
                                f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} {display_num} {lang}\n╚═══════════════╝"
                            )
                            inbox_kb = {"inline_keyboard": [[
                                {
                                    "text": str(otp),
                                    "icon_custom_emoji_id": "5353022963132174959",
                                    "copy_text": {"text": str(otp)},
                                    "style": "success",
                                }
                            ]]}
                            reward = float(bot_settings.get("otp_reward", 0.0))
                            if reward > 0:
                                update_balance(owner_id, reward)
                                inbox_kb["inline_keyboard"].append([{"text": f"Added {reward} tk", "callback_data": "ignore", "style": "primary"}])
                            send_message(owner_id, inbox_msg, reply_markup=inbox_kb)
                            increment_user_otp_count(owner_id)

                        save_db()
                    except Exception as e:
                        safe_print(f"OTP process error: {e}")
        except Exception as e:
            safe_print(f"Panel monitor loop error: {e}")
        time.sleep(5)


# ==========================================
# User Management
# ==========================================
user_cache = {}

def get_user(user_id):
    uid_str = str(user_id)
    if uid_str in user_cache: 
        return user_cache[uid_str]
    
    if uid_str in users_db:
        data = users_db[uid_str]
        if "total_otps" not in data: data["total_otps"] = 0
        if "daily_otps" not in data: data["daily_otps"] = 0
        if "banned" not in data: data["banned"] = False
        if "verified" not in data: data["verified"] = False
        user_cache[uid_str] = data
        return data
    else:
        new_user = {
            "user_id": int(user_id), 
            "balance": 0.0, 
            "total_refers": 0, 
            "total_otps": 0,
            "daily_otps": 0,
            "banned": False, 
            "verified": False,
            "referred_by": None,
            "ref_paid": False
        }
        users_db[uid_str] = new_user
        user_cache[uid_str] = new_user
        save_db()
        return new_user

def update_balance(user_id, amount):
    uid_str = str(user_id)
    u_data = get_user(uid_str)
    u_data["balance"] = round(u_data.get("balance", 0.0) + float(amount), 2)
    users_db[uid_str] = u_data
    user_cache[uid_str] = u_data
    save_db()

# ==========================================
# UI Keyboards & Menu Builders
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    kb = []
    for row in bot_settings.get("main_keyboard_layout", []):
        kb_row = []
        for btn in row:
            if btn.get("enabled", True):
                btn_obj = {"text": btn["text"]}
                if "icon_custom_emoji_id" in btn:
                    btn_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                if "style" in btn:
                    btn_obj["style"] = btn["style"]
                kb_row.append(btn_obj)
        if kb_row:
            kb.append(kb_row)
            
    if is_admin(user_id): 
        kb.append([{"text": "Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}

def get_admin_text():
    users_count = len(all_known_users)
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "DAILY LEADERBOARD", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"},
         {"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "Used number", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "show_used", "style": "success"},
         {"text": "Unused number", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Stex Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_control", "style": "success"},
         {"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"}],
        [{"text": "Zenex Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "zenex_control", "style": "danger"},
         {"text": "Mino Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "mino_control", "style": "success"}],
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}], 
        [{"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"},
         {"text": "Button Mgmt", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_btn_layout", "style": "success"}],
        [{"text": "SNZ Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "snz_control", "style": "primary"},
         {"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}], 
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

# ==========================================
# Dynamic Button Management Keyboards
# ==========================================
def button_mgmt_keyboard():
    return {"inline_keyboard": [
        [{"text": "Button On/Off Status", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "btn_mgmt_status", "style": "primary"}],
        [{"text": "Button Rearrange (Up/Down/Left/Right)", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "btn_mgmt_rearrange", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def button_status_keyboard():
    kb = []
    for row in bot_settings.get("main_keyboard_layout", []):
        for btn in row:
            status = "🟢 ON" if btn.get("enabled", True) else "🔴 OFF"
            kb.append([
                {"text": f"{btn['text']} ({status})", "callback_data": f"btn_toggle_status_{btn['text']}", "style": "primary"}
            ])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_btn_layout", "style": "danger"}])
    return {"inline_keyboard": kb}

def button_rearrange_list_keyboard():
    kb = []
    for row in bot_settings.get("main_keyboard_layout", []):
        kb_row = []
        for btn in row:
            kb_row.append({"text": btn["text"], "callback_data": f"btn_select_move_{btn['text']}", "style": "primary"})
        kb.append(kb_row)
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_btn_layout", "style": "danger"}])
    return {"inline_keyboard": kb}

def button_movement_keyboard(target_text):
    return {"inline_keyboard": [
        [
            {"text": "⬆️ Up", "callback_data": f"btn_move_up_{target_text}", "style": "primary"},
            {"text": "⬇️ Down", "callback_data": f"btn_move_down_{target_text}", "style": "primary"}
        ],
        [
            {"text": "⬅️ Left", "callback_data": f"btn_move_left_{target_text}", "style": "primary"},
            {"text": "➡️ Right", "callback_data": f"btn_move_right_{target_text}", "style": "primary"}
        ],
        [
            {"text": "➕ New Row Above", "callback_data": f"btn_new_row_above_{target_text}", "style": "success"},
            {"text": "➕ New Row Below", "callback_data": f"btn_new_row_below_{target_text}", "style": "success"}
        ],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "btn_mgmt_rearrange", "style": "danger"}]
    ]}

def get_user_management_text():
    total = len(all_known_users)
    verified = sum(1 for u in users_db.values() if u.get("verified") or u.get("total_otps", 0) > 0)
    banned = sum(1 for u in users_db.values() if u.get("banned"))
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: {verified}
🚫 BANNED USERS: {banned}
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"},
         {"text": "Edit Search Number", "icon_custom_emoji_id": "5190645917711114179", "callback_data": "md_edit_search_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit TRAFFIC", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "md_edit_traffic", "style": "primary"},
         {"text": "Edit Refer", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Edit WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "md_edit_withdrawal", "style": "danger"},
         {"text": "Edit SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "md_edit_support", "style": "danger"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}

def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        enabled = btn.get("enabled", True)
        status_icon = "🟢" if enabled else "🔴"
        btn_txt = btn['text']
        kb.append([
            {"text": f"{status_icon} {btn_txt}", "callback_data": f"md_togbtn_{menu_key}_{idx}", "style": "primary"},
            {"text": "🗑 Delete", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}
        ])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        kb.append([{"text": f"Delete: {ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    normalize_fw_groups()
    kb = [[{"text": "Edit OTP Button Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}]]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def stex_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add Stex Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_stex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_stex_keys", "style": "danger"}],
        [{"text": "Manage Stex Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_stex_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def voltx_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def zenex_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add Zenex Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_zenex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_zenex_keys", "style": "danger"}],
        [{"text": "Manage Zenex Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_zenex_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "zenex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def mino_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add Mino Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_mino_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_mino_keys", "style": "danger"}],
        [{"text": "Manage Mino Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_mino_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "mino_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def snz_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    sup_status = "ON" if bot_settings.get("support_link") else "OFF"
    grp_status = "ON" if bot_settings.get("w_group") else "OFF"
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "snz_toggle_w", "style": "primary"}],
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "snz_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "snz_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "snz_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "snz_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "snz_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "snz_num_share", "style": "primary"}],
        [{"text": f"SUPPORT LINK: {sup_status}", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "snz_sup_link", "style": "success"},
         {"text": "W. METHODS", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. GROUP: {grp_status}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "snz_w_group", "style": "success"},
         {"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        kb.append([{"text": f"Delete: {m}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "snz_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def panels_list_keyboard():
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703"
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    kb.append([{"text": "Add Panel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_panel", "style": "success"}])
    kb.append([{"text": "Delete Panel", "icon_custom_emoji_id": "5336944168944047463", "callback_data": "list_del_panels", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    is_cr = is_cr_api_panel(p)
    if not is_cr:
        kb.append([{"text": "Update Curl", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"upd_curl_{idx}", "style": "primary"}])
    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Panel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}

def build_traffic_ui():
    global recent_traffic
    current_time = time.time()
    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
    
    stats = {}
    for t in recent_traffic:
        srv = t.get("service", "Unknown")
        iso = t.get("iso", "XX")
        flag = t.get("flag", "🌍")
        
        if srv not in stats:
            stats[srv] = {}
        if iso not in stats[srv]:
            stats[srv][iso] = {"count": 0, "flag": flag}
        stats[srv][iso]["count"] += 1
        
    txt = "╔═════════════════╗\n║  📈 <b>NETWORK TRAFFIC</b>\n╚═════════════════╝\n\n"
    kb = []
    if not stats:
        txt += "<i>No recent traffic found in the last hour...</i>\n"
    else:
        srv_totals = []
        for srv, countries in stats.items():
            total = sum(c["count"] for c in countries.values())
            srv_totals.append((srv, total, countries))
        
        srv_totals.sort(key=lambda x: x[1], reverse=True)
        
        for srv, total, countries in srv_totals:
            app_full_name, prem_app_html = get_service_info_html(srv)
            txt += f"[ {prem_app_html} <b>{app_full_name}</b> ]\n│\n"
            c_list = sorted(countries.items(), key=lambda x: x[1]["count"], reverse=True)
            c_list = c_list[:7] 
            
            for i, (iso, c_data) in enumerate(c_list):
                prem_flag_html = get_flag_info_html(iso)
                count = c_data["count"]
                
                c_name = iso
                for code, fdata in bot_settings.get("premium_flags", {}).items():
                    if fdata.get("iso") == iso:
                        c_name = fdata.get("name", iso)
                        break
                        
                txt += f"├ {prem_flag_html} <b>{c_name} ({iso})</b>\n"
                txt += f"│ ╰ Success: {count}\n"
                if i < len(c_list) - 1:
                    txt += "│\n"
            txt += "\n"
        
        for srv, _, _ in srv_totals: 
            safe_srv = srv[:20] 
            app_full_name, _ = get_service_info_html(safe_srv, safe_srv)
            kb.append([{"text": f"Explore {app_full_name} Range", "icon_custom_emoji_id": "5190645917711114179", "callback_data": f"exp_rng_{safe_srv}", "style": "success"}])
            
    txt = render_body_text(txt)
    kb.append([{"text": "Refresh", "icon_custom_emoji_id": "5465368548702446780", "callback_data": "refresh_traffic", "style": "primary"}])
    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
    return txt, {"inline_keyboard": kb}

# ==========================================
# Message Handler
# ==========================================
def handle_message(msg):
    global total_uploaded_stats, total_assigned_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    
    if chat_type != "private":
        return
        
    text = msg.get("text", "")
    register_user_local(chat_id)

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    
    # Block Disabled buttons execution
    is_disabled = False
    for row in bot_settings.get("main_keyboard_layout", []):
        for btn in row:
            if btn["text"].strip().lower() == text.strip().lower() and not btn.get("enabled", True):
                is_disabled = True
                break
    if is_disabled:
        send_message(chat_id, render_body_text("⚠️ <b>This feature is currently disabled!</b>"))
        return

    # Process invitation parameter if any
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                uid_str = str(chat_id)
                if uid_str not in users_db:
                    get_user(chat_id)
                    users_db[uid_str]["referred_by"] = inviter
                    users_db[uid_str]["ref_paid"] = False
                    save_db()
                        
    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
        
    MAIN_MENU_CMDS = ["GET NUMBER", "Search Number", "TRAFFIC", "Refer", "WITHDRAWAL", "SUPPORT", "Admin Panel", "2FA ONLINE"]
    
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True
    
    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]
        
        if state == "wait_for_add_panel" and text:
            curl_parsed = parse_curl_command(text)
            if not curl_parsed:
                send_message(chat_id, render_body_text(
                    f"{PEM['no']} Invalid curl! Browser থেকে <b>Copy as cURL</b> করে paste করুন (PHPSESSID সহ)."
                ), reply_markup=get_cancel_kb())
                return

            action, panel, was_replaced = smart_add_or_update_panel(curl_parsed)
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            url_key = curl_url_key(curl_parsed["url"])
            sess_id = curl_parsed.get("cookies", {}).get("PHPSESSID", "")
            p_idx = next((i for i, ep in enumerate(bot_settings["panels"]) if ep.get("curl_url_key") == panel.get("curl_url_key")), None)

            if action == "updated":
                status_txt = (
                    f"{PEM['ok']} <b>PHPSESSID updated!</b>\n\n"
                    f"🔗 URL: <code>{url_key}</code>\n"
                    f"🔐 PHPSESSID: <code>{sess_id[:16]}...</code>\n"
                    f"📡 Panel <b>{panel['name']}</b> will fetch OTP again."
                )
            else:
                status_txt = (
                    f"{PEM['ok']} <b>Panel added!</b>\n\n"
                    f"📛 Name: <b>{panel['name']}</b>\n"
                    f"🔗 URL: <code>{url_key}</code>\n"
                    f"🔐 PHPSESSID: <code>{sess_id[:16]}...</code>\n"
                    f"💾 Saved in <code>phpsseid.json</code>"
                )

            if temp_data[chat_id].get("p_idx") is not None and p_idx is not None:
                edit_message(chat_id, msg_id, render_body_text(panel_config_text(panel)), reply_markup=panel_config_keyboard(p_idx))
            else:
                edit_message(chat_id, msg_id, render_body_text(status_txt), reply_markup=panels_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        # User Management Flows
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID! Please send a numeric User ID."), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if target_uid_str in users_db:
                current_bal = users_db[target_uid_str].get('balance', 0.0)
                temp_data[chat_id]["target_uid"] = target_uid
                user_states[chat_id] = "wait_for_um_bal_amt"
                send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {current_bal} ৳\n\n📝 Send the amount to ADD (e.g. 50) or REMOVE (e.g. -50):"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip())
                target_uid = temp_data[chat_id]["target_uid"]
                update_balance(target_uid, amt)
                send_message(chat_id, render_body_text(f"{PEM['ok']} Balance updated successfully for {target_uid}!"), reply_markup=main_menu(chat_id))
                send_message(target_uid, render_body_text(f"🔔 Your balance has been adjusted by <b>{amt} ৳</b> by an Admin."))
                del user_states[chat_id]
                del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount! Please send a number."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if target_uid_str in users_db:
                current_status = users_db[target_uid_str].get("banned", False)
                new_status = not current_status
                users_db[target_uid_str]["banned"] = new_status
                save_db()
                
                user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
                status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
                send_message(chat_id, render_body_text(f"✅ User {target_uid} has been {status_text}!"), reply_markup=main_menu(chat_id))
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if target_uid_str in users_db:
                data = users_db[target_uid_str]
                is_verified = True if data.get('total_otps', 0) > 0 else data.get('verified', False)
                prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {data.get('balance', 0.0)} ৳
🤝 Total Refers: {data.get('total_refers', 0)}
🔐 Total OTPs: {data.get('total_otps', 0)}
✅ Verified: {is_verified}
🚫 Banned: {data.get('banned', False)}
➖➖➖➖➖➖➖➖"""
                kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
                send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
            return

        # Menu Design Flow
        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                formatted_html_text = extract_premium_html(msg)
                bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                save_db()
                
                delete_message(chat_id, msg["message_id"])
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Message Body Updated successfully!</b>\n\n🎨 <b>Editing: {menu_key.upper()}</b>\n\nPreview of current Text:\n{preview_text}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                send_message(chat_id, f"❌ Error saving text: {e}")
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
            
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    
                    emoji_id = None
                    emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0)
                            length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                            break
                            
                    if emoji_char:
                        btn_text = btn_text.replace(emoji_char, "").strip()
                        
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary", "enabled": True}
                    if emoji_id:
                        btn_data["icon_custom_emoji_id"] = emoji_id
                        
                    bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['gear']} <b>Edit Inline Buttons: {menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format. Use <code>Button Text - https://link.com</code>"))
            except: pass
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 Send the Number (e.g. +8801712345678):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 Send the OTP (e.g. 556677):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 Send the Language (e.g. EN, AR):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"):
                lang = "#" + lang
                
            srv = temp_data[chat_id]["service"]
            num = temp_data[chat_id]["number"]
            otp = temp_data[chat_id]["otp"]
            
            masked = mask_number(num)
            prem_flag_html = get_flag_info_html(num)
            char, iso = get_flag_and_code(num)
            app_full_name, prem_app_html = get_service_info_html(srv)
            
            test_sms = f"{otp} is your {app_full_name} code"
            msg_text = build_group_otp_message(num, otp, test_sms, prem_app_html, app_full_name)
            
            forward_otp_to_groups(msg_text, otp, num=num)
                
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test message formatted and sent to all Forward Groups!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_emoji_extract":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode('utf-16-le')
                    emoji_text = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                    break
            
            if custom_emoji_id:
                temp_data[chat_id] = {"id": custom_emoji_id, "char": emoji_text}
                user_states[chat_id] = "wait_for_emoji_details"
                send_message(chat_id, render_body_text(f"{PEM['ok']} Emoji ID পাওয়া গেছে: <code>{custom_emoji_id}</code>\n\n📌 এখন এটি সেভ করার জন্য টাইপ এবং নাম লিখুন।\n\n<b>ফরমেট:</b>\n`FLAG | 880 | BD | Bangladesh`\nঅথবা\n`APP | WhatsApp`"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} কোনো Premium Emoji পাওয়া যায়নি! দয়া করে Custom Emoji সেন্ড করুন।"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_emoji_details" and text:
            parts = [p.strip() for p in text.split("|")]
            mode = parts[0].upper()
            eid = temp_data[chat_id]["id"]
            char = temp_data[chat_id]["char"]
            
            if mode == "FLAG" and len(parts) == 4:
                code, iso, name = parts[1], parts[2], parts[3]
                bot_settings["premium_flags"][code] = {"char": char, "iso": iso.upper(), "name": name, "id": eid}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Flag Emoji সেভ হয়েছে!\nCode: {code} | Name: {name}"), reply_markup=emoji_settings_keyboard())
            elif mode == "APP" and len(parts) == 2:
                name = parts[1]
                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name.title()}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} App Emoji সেভ হয়েছে!\nName: {name}"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} ফরম্যাট ভুল!\n\nসঠিক ফরম্যাট:\n`FLAG | 880 | BD | Bangladesh`\n`APP | WhatsApp`"))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            content = requests.get(f"{FILE_URL}{file_path}").text
            
            mode = "flags" if state == "wait_for_flag_txt" else "apps"
            count = 0
            
            if mode == "flags":
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            prefix_str = line[:json_match.start()].strip()
                            code_match = re.search(r'\((\d+)\)', prefix_str)
                            iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                            
                            if code_match and iso_match and char and eid:
                                code = code_match.group(1)
                                iso = iso_match.group(1).upper()
                                name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                count += 1
                        except: pass
            else:
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            name_part = line[:json_match.start()].strip()
                            name = name_part.replace(char, '').strip() if char else name_part
                            if char and eid and name:
                                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                count += 1
                        except: pass
            
            save_db()
            send_message(chat_id, render_body_text(f"{PEM['ok']} Successfully loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            del user_states[chat_id]
            return

        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id)).start()
            del user_states[chat_id]
            return

        elif state == "wait_for_txt" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"{FILE_URL}{file_path}").text
            
            temp_data[chat_id] = {"numbers": file_content.splitlines(), "filename": doc["file_name"]}
            user_states[chat_id] = "wait_for_service"
            send_message(chat_id, render_body_text(f"{PEM['ok']} File received.\n\n📌 Enter the service name (e.g., WHATSAPP):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_service" and text:
            temp_data[chat_id]["service"] = text.upper()
            user_states[chat_id] = "wait_for_country"
            send_message(chat_id, render_body_text(f"{PEM['ok']} Service set.\n\n🌍 Enter the country name (e.g., YEMEN):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_country" and text:
            country = text.upper()
            service = temp_data[chat_id]["service"]
            raw_numbers = temp_data[chat_id]["numbers"]

            clean_nums = []
            for num in raw_numbers:
                num = num.strip()
                if num:
                    if not num.startswith('+'): num = '+' + num
                    clean_nums.append(num)

            batch_id = str(uuid.uuid4())[:8]
            number_batches[batch_id] = {"filename": temp_data[chat_id]["filename"], "service": service, "country": country, "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]}
            total_uploaded_stats += len(clean_nums)
            save_db()

            send_message(chat_id, render_body_text(f"{PEM['ok']} Numbers added to local stock! ({len(clean_nums)} numbers)"))

            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_stex_key" and text:
            bot_settings["stex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Stex API Key Added! Total Keys: {len(bot_settings.get('stex_keys', []))}"), reply_markup=stex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_voltx_key" and text:
            bot_settings["voltx_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Voltx API Key Added! Total Keys: {len(bot_settings.get('voltx_keys', []))}"), reply_markup=voltx_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_zenex_key" and text:
            bot_settings["zenex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Zenex API Key Added! Total Keys: {len(bot_settings.get('zenex_keys', []))}"), reply_markup=zenex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_mino_key" and text:
            bot_settings["mino_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Mino API Key Added! Total Keys: {len(bot_settings.get('mino_keys', []))}"), reply_markup=mino_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
            bot_settings["search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            kb = []
            for idx, c in enumerate(bot_settings.get("search_countries", [])):
                kb.append([{"text": f"❌ Delete {c}", "callback_data": f"del_sc_{idx}", "style": "danger"}])
            kb.append([{"text": "➕ Add Country Code", "callback_data": "add_search_country", "style": "success"}])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
            bot_settings["voltx_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "voltx_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_zsc" and text:
            code = text.strip().replace("+", "")
            if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
            bot_settings["zenex_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "zenex_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_msc" and text:
            code = text.strip().replace("+", "")
            if "mino_search_countries" not in bot_settings: bot_settings["mino_search_countries"] = []
            bot_settings["mino_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "mino_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_sx_srv_name" and text:
            srv = text.strip().upper()
            if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
            if srv not in bot_settings["stex_services"]: bot_settings["stex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_stex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_sx_cnt_name" and text:
            cnt = text.strip().upper()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["stex_services"][srv]: bot_settings["stex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"sx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_sx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["stex_services"][srv][cnt]:
                bot_settings["stex_services"][srv][cnt].append(new_range)
                if "search_countries" not in bot_settings:
                    bot_settings["search_countries"] = []
                if new_range not in bot_settings["search_countries"]:
                    bot_settings["search_countries"].append(new_range)
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"sx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_srv_name" and text:
            srv = text.strip().upper()
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            if srv not in bot_settings["voltx_services"]: bot_settings["voltx_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_voltx_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip().upper()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["voltx_services"][srv]: bot_settings["voltx_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].append(new_range)
                if "voltx_search_countries" not in bot_settings:
                    bot_settings["voltx_search_countries"] = []
                if new_range not in bot_settings["voltx_search_countries"]:
                    bot_settings["voltx_search_countries"].append(new_range)
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_srv_name" and text:
            srv = text.strip().upper()
            if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
            if srv not in bot_settings["zenex_services"]: bot_settings["zenex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_zenex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_cnt_name" and text:
            cnt = text.strip().upper()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["zenex_services"][srv]: bot_settings["zenex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["zenex_services"][srv][cnt]:
                bot_settings["zenex_services"][srv][cnt].append(new_range)
                if "zenex_search_countries" not in bot_settings:
                    bot_settings["zenex_search_countries"] = []
                if new_range not in bot_settings["zenex_search_countries"]:
                    bot_settings["zenex_search_countries"].append(new_range)
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_mn_srv_name" and text:
            srv = text.strip().upper()
            if "mino_services" not in bot_settings: bot_settings["mino_services"] = {}
            if srv not in bot_settings["mino_services"]: bot_settings["mino_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_mino_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_mn_cnt_name" and text:
            cnt = text.strip().upper()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["mino_services"][srv]: bot_settings["mino_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"mn_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_mn_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["mino_services"][srv][cnt]:
                bot_settings["mino_services"][srv][cnt].append(new_range)
                if "mino_search_countries" not in bot_settings:
                    bot_settings["mino_search_countries"] = []
                if new_range not in bot_settings["mino_search_countries"]:
                    bot_settings["mino_search_countries"].append(new_range)
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"mn_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_wm" and text:
            bot_settings["w_methods"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fj" and text:
            bot_settings["fj_channels"].append(parse_chat_id(text))
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🔗 <b>FORCE JOIN SYSTEM</b>\nManage channels below:\n<i>(Note: For private links, use numeric IDs like -100...)</i>"), reply_markup=fj_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                bot_settings["admins"].append(int(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fw_id" and text:
            gid = text.strip()
            normalize_fw_groups()
            if any(get_fw_chat_id(x) == gid for x in bot_settings["fw_groups"]):
                send_message(chat_id, render_body_text(f"{PEM['no']} This group is already added!"), reply_markup=get_cancel_kb())
                return
            bot_settings["fw_groups"].append({"chat_id": gid, "buttons": []})
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp_data[chat_id]["fw_idx"]
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                
                emoji_id = None
                emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0)
                        length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                
                if emoji_char:
                    btn_text = btn_text.replace(emoji_char, "").strip()
                    
                btn_data = {"text": btn_text, "url": btn_url, "enabled": True}
                if emoji_id:
                    btn_data["icon_custom_emoji_id"] = emoji_id
                    
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][fw_idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        # SNZ Control Handlers
        elif state == "set_snz":
            msg_id = temp_data[chat_id]["msg_id"]
            key = temp_data[chat_id]["key"]
            try:
                if key in ["min_withdraw", "otp_reward", "refer_reward"]: bot_settings[key] = float(text)
                elif key in ["cooldown", "num_req", "num_share"]: bot_settings[key] = int(text)
                else: bot_settings[key] = text
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>SNZ CONTROL PANEL</b>"), reply_markup=snz_control_keyboard())
            except:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>SNZ CONTROL PANEL</b>\n\n❌ Invalid value!"), reply_markup=snz_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text("❌ Please enter a valid 3 to 9 digit number!"))
                return
                
            wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = wait_msg.get("result", {}).get("message_id")
            
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data.get("numbers", [])):
                    if str(n_obj.get("num", "")).replace("+", "").startswith(query) and not user_already_used_number(n_obj, chat_id):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            api_source = None
            if not found_indices:
                allowed_provs = allowed_providers_for_query(query)
                
                if not allowed_provs:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ This country code is not allowed!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                    
                if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
                
                req_count = bot_settings.get("num_req", 1)
                fetched_nums, api_source = fetch_numbers_from_api(
                    query, chat_id,
                    prefer=allowed_provs[0],
                    req_count=req_count,
                )
                if fetched_nums:
                    total_assigned_stats += len(fetched_nums)
                        
                if not fetched_nums:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Number out of stock!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    fetched_nums.append(num_str)
                    
                    n_obj["shares"] += 1
                    n_obj.setdefault("used_by", []).append(chat_id)
                    total_assigned_stats += 1
                    
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            for num in fetched_nums:
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                emoji_id = get_flag_emoji_id(display_num)
                kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
                
            ext = PROVIDER_SUFFIX.get(api_source, "")
            
            kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5465368548702446780", "callback_data": f"c_n_s_{query}{ext}", "style": "danger"},
                       {"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "url": bot_settings["otp_link"], "style": "primary"}])
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                if c_b.get("enabled", True):
                    b_copy = c_b.copy()
                    if "style" not in b_copy: b_copy["style"] = "primary"
                    kb.append([b_copy])
            
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            res_s = edit_blank_keyboard(chat_id, wait_msg_id, {"inline_keyboard": kb}, build_assigned_text(fetched_nums)) if wait_msg_id else None
            if res_s and res_s.get("ok"):
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums}
            else:
                msg_res = send_blank_keyboard(chat_id, {"inline_keyboard": kb}, build_assigned_text(fetched_nums))
                if msg_res and "result" in msg_res:
                    user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums}
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
            return
            
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = float(text.strip())
                bal = temp_data[chat_id]["balance"]
                min_w = bot_settings['min_withdraw']
                
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Minimum withdrawal is {min_w} ৳!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ You don't have enough balance!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                    
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"✅ Amount: {amount} ৳\n\n📱 Now send your <b>{temp_data[chat_id]['method']}</b> account number:"), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount!\n\n📝 Please send a valid number:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
            delete_message(chat_id, msg.get("message_id"))

            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error: Message not found. Try again."))
                del user_states[chat_id]
                return

            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret)
                code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                
                success_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"《 🔐 <b>2FA CODE</b> 》\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                    f"━━━━━━━━━━━━━━━"
                )
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            except Exception:
                error_txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━\n❌ <b>Invalid Secret Key! Try again.</b>\n━━━━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            method = temp_data[chat_id]["method"]
            amount = temp_data[chat_id]["amount"]
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            update_balance(chat_id, -amount)
            pending_withdrawals[req_id] = {"user_id": chat_id, "amount": amount, "method": method, "number": number, "full_name": full_name}
            
            withdrawals_db[req_id] = {
                "req_id": req_id,
                "user_id": str(chat_id),
                "amount": amount,
                "method": method,
                "number": number,
                "full_name": full_name,
                "status": "pending",
                "timestamp_raw": time.time()
            }
            save_db()
                
            if bot_settings["w_group"]:
                admin_msg = f"🎙 <b>NEW WITHDRAWAL REQUEST</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={chat_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amount} TK\n🍏 <b>NUMBER:</b> <code>{number}</code>\n🏦 <b>METHOD:</b> {method}\n\n🧾 <b>REQ ID:</b> {req_id}\n👑 <b>PROCESSED BY ADMIN</b>"
                kb = {"inline_keyboard": [[{"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"}, {"text": "REJECT", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrej_{req_id}", "style": "danger"}]]}
                send_message(bot_settings["w_group"], render_body_text(admin_msg), reply_markup=kb)
            
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            success_text = f"{PEM['ok']} Your withdrawal request has been submitted!\n\n🧾 <b>Req ID:</b> {req_id}\n💰 <b>Amount:</b> {amount} ৳\n🏦 <b>Method:</b> {method}\n📱 <b>Number:</b> <code>{number}</code>"
            
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return

    # Regular Commands
    if text.startswith("/start"):
        get_user(chat_id)
        uid_str = str(chat_id)
        if uid_str in users_db:
            u_data = users_db[uid_str]
            if u_data.get("referred_by") and not u_data.get("ref_paid"):
                inviter = u_data["referred_by"]
                u_data["ref_paid"] = True
                users_db[uid_str] = u_data
                
                reward = bot_settings.get("refer_reward", 0.2)
                update_balance(inviter, reward)
                
                inv_uid_str = str(inviter)
                if inv_uid_str in users_db:
                    users_db[inv_uid_str]["total_refers"] = users_db[inv_uid_str].get("total_refers", 0) + 1
                    
                save_db()
                ref_msg = (
                    f"{PEM['gift']} <b>New Referral !</b>\n"
                    f"------------------\n"
                    f"🔥 <b>You Received {reward} TK</b>\n"
                    f"------------------\n"
                    f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                )
                send_message(inviter, render_body_text(ref_msg))
                    
        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        kb = []
        for b in c_msg.get("buttons", []):
            if b.get("enabled", True):
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
        
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))
            
    elif text == "TRAFFIC":
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)
        
    elif text == "Refer":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        
        raw_txt = c_msg.get("text", f"{PEM['gift']} Refer").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", str(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []): 
            if b.get("enabled", True):
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "WITHDRAWAL":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} Withdrawals are currently disabled."))
            return
        
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get('total_otps', 0))).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{min_w}", str(bot_settings['min_withdraw']))
        txt = render_body_text(raw_txt)
        
        kb = []
        for m in bot_settings["w_methods"]:
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        
        for b in c_msg.get("buttons", []): 
            if b.get("enabled", True):
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Admin Panel" and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text == "GET NUMBER":
        local_srvs = set([b["service"] for b in number_batches.values() if b.get("numbers")])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        zx_srvs = set(bot_settings.get("zenex_services", {}).keys())
        mn_srvs = set(bot_settings.get("mino_services", {}).keys())
        all_services = local_srvs.union(stex_srvs).union(voltx_srvs).union(zx_srvs).union(mn_srvs)
        total_local = sum(len(b.get("numbers", [])) for b in number_batches.values())
        
        if not all_services:
            send_message(chat_id, render_body_text(f"{PEM['no']} No numbers or services available!\nLocal stock: <b>0</b>\nUpload numbers from Admin Panel."))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            base = c_msg.get("text", f"{PEM['pin']} Select Service")
            txt = render_body_text(f"{base}\n\n📦 Local stock: <b>{total_local}</b>")
            
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            for s in sorted(all_services, key=lambda x: str(x).upper()):
                emoji_id = "5352694861990501856"
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                left = sum(len(b.get("numbers", [])) for b in number_batches.values() if str(b.get("service", "")).upper() == str(s).upper())
                label = f"{s} ({left})" if left else str(s)
                kb.append([{"text": label, "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"}])
            
            for b in c_msg.get("buttons", []): 
                if b.get("enabled", True):
                    b_copy = b.copy()
                    if "style" not in b_copy: b_copy["style"] = "primary"
                    kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Search Number":
        user_states[chat_id] = "wait_for_search"
        c_msg = bot_settings["custom_messages"].get("search_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['num']} Search Number"))
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]
        for b in c_msg.get("buttons", []): 
            if b.get("enabled", True):
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif text == "SUPPORT":
        c_msg = bot_settings["custom_messages"].get("support", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['msg']} Support"))
        if not txt.strip(): txt = render_body_text(f"{PEM['msg']} Support")
        kb = []
        for b in c_msg.get("buttons", []):
            if b.get("enabled", True):
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            
        sup_link = bot_settings.get("support_link", "")
        if sup_link:
            kb.insert(0, [{"text": "Contact Support", "icon_custom_emoji_id": "5337302974806922068", "url": sup_link, "style": "success"}])
            
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb} if kb else None)

def expire_previous_number(chat_id):
    if chat_id in user_active_sessions:
        prev_data = user_active_sessions[chat_id]
        prev_msg_id = prev_data["msg_id"]
        nums = prev_data["nums"]
        
        for num in nums:
            if num in stex_assigned_numbers:
                del stex_assigned_numbers[num]
            if num in voltx_assigned_numbers:
                del voltx_assigned_numbers[num]
            if num in zenex_assigned_numbers:
                del zenex_assigned_numbers[num]
            if num in mino_assigned_numbers:
                del mino_assigned_numbers[num]
        save_db()
        
        kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
        try:
            edit_blank_keyboard(chat_id, prev_msg_id, {"inline_keyboard": kb})
        except:
            pass
        del user_active_sessions[chat_id]

def _norm_key(s):
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())

def _known_services():
    srvs = set()
    for b in number_batches.values():
        if b.get("service"):
            srvs.add(str(b["service"]))
    srvs.update(bot_settings.get("stex_services", {}).keys())
    srvs.update(bot_settings.get("voltx_services", {}).keys())
    srvs.update(bot_settings.get("zenex_services", {}).keys())
    srvs.update(bot_settings.get("mino_services", {}).keys())
    return srvs

def parse_service_country_callback(data, prefix):
    """Parse g_c_SERVICE_COUNTRY / c_n_SERVICE_COUNTRY (country may contain underscores)."""
    if not data.startswith(prefix):
        return None, None
    rest = data[len(prefix):]
    if not rest:
        return None, None
    known = _known_services()
    for srv in sorted(known, key=len, reverse=True):
        if rest == srv:
            return srv, ""
        if rest.startswith(srv + "_"):
            return srv, rest[len(srv) + 1:]
    parts = rest.split("_", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""

def user_already_used_number(n_obj, chat_id):
    if not isinstance(n_obj, dict):
        return False
    used = n_obj.get("used_by", []) or []
    cid = str(chat_id)
    return any(str(u) == cid for u in used)

stock_lock = threading.Lock()

def find_local_stock_indices(service, country, chat_id):
    """Match local batches by service+country (normalized), then soft country, then service-only."""
    available = []
    svc_n = _norm_key(service)
    cty_n = _norm_key(country)

    def collect(match_country="exact"):
        out = []
        for b_id, b_data in number_batches.items():
            if _norm_key(b_data.get("service")) != svc_n:
                continue
            b_cty = _norm_key(b_data.get("country"))
            if match_country == "exact":
                if cty_n and b_cty != cty_n:
                    continue
            elif match_country == "soft":
                if not cty_n or not b_cty or not (cty_n in b_cty or b_cty in cty_n):
                    continue
            # match_country == "service": any country
            for idx, n_obj in enumerate(b_data.get("numbers", [])):
                if isinstance(n_obj, dict) and n_obj.get("num") and not user_already_used_number(n_obj, chat_id):
                    out.append((b_id, idx))
        return out

    available = collect("exact")
    if available:
        return available
    available = collect("soft")
    if available:
        return available
    # Last resort: any unused number for this service (keeps GET NUMBER working)
    return collect("service")

def count_local_stock(service=None, country=None):
    svc_n = _norm_key(service) if service else None
    cty_n = _norm_key(country) if country else None
    total = 0
    for b in number_batches.values():
        if svc_n and _norm_key(b.get("service")) != svc_n:
            continue
        if cty_n and _norm_key(b.get("country")) != cty_n:
            continue
        total += sum(1 for n in (b.get("numbers") or []) if isinstance(n, dict) and n.get("num"))
    return total

API_PROVIDERS = ["stex", "voltx", "zenex", "mino"]
PROVIDER_SUFFIX = {"stex": "_stex", "voltx": "_vtx", "zenex": "_zx", "mino": "_mn"}
PROVIDER_NAMES = {"stex": "Stex", "voltx": "Voltx", "zenex": "Zenex", "mino": "Mino"}

def provider_keys(label):
    return bot_settings.get(f"{label}_keys", []) or []

def provider_services(label):
    return bot_settings.get(f"{label}_services", {}) or {}

def provider_search_countries(label):
    k = "search_countries" if label == "stex" else f"{label}_search_countries"
    return bot_settings.get(k, []) or []

def provider_assigned(label):
    return {"stex": stex_assigned_numbers, "voltx": voltx_assigned_numbers,
            "zenex": zenex_assigned_numbers, "mino": mino_assigned_numbers}[label]

def allowed_providers_for_query(query):
    """Providers whose allowed-range list matches this search query."""
    q = str(query)
    return [l for l in API_PROVIDERS if any(q.startswith(str(c)) for c in provider_search_countries(l))]

def split_provider_suffix(data):
    """'c_n_s_224_INSTAGRAM_zx' -> ('c_n_s_224_INSTAGRAM', 'zenex')."""
    for label, suf in PROVIDER_SUFFIX.items():
        if data.endswith(suf):
            return data[:-len(suf)], label
    return data, None

def get_api_ranges_for(service, country):
    """Return {provider: [ranges]} with normalized country lookup."""
    svc_n = _norm_key(service)
    cty_n = _norm_key(country)
    out = {l: [] for l in API_PROVIDERS}
    for label in API_PROVIDERS:
        for srv, countries in provider_services(label).items():
            if _norm_key(srv) != svc_n:
                continue
            for cnt, ranges in (countries or {}).items():
                if (not cty_n or _norm_key(cnt) == cty_n or cty_n in _norm_key(cnt) or _norm_key(cnt) in cty_n) and ranges:
                    out[label].extend(ranges)
    return out

def _digits_only(v):
    return re.sub(r"\D", "", str(v or ""))

def _find_number_in(obj, depth=0):
    """Find a phone number in an unknown JSON response."""
    if depth > 4:
        return ""
    if isinstance(obj, dict):
        for k in ("full_number", "no_plus_number", "number", "phone_number", "phone", "msisdn", "num", "national_number"):
            if k in obj:
                d = _digits_only(obj.get(k))
                if len(d) >= 7:
                    return d
        for v in obj.values():
            if isinstance(v, (dict, list)):
                d = _find_number_in(v, depth + 1)
                if d:
                    return d
    elif isinstance(obj, list):
        for v in obj:
            d = _find_number_in(v, depth + 1)
            if d:
                return d
    return ""

def _pad_range(rng):
    r = str(rng).strip()
    return r if "X" in r.upper() else r + "XXX"

def _request_number(label, api_key, rng, timeout):
    """Ask one provider for ONE number. Returns digits-only string or ''."""
    if label in ("stex", "voltx"):
        base = STEX_BASE_URL if label == "stex" else VOLTX_BASE_URL
        res = requests.post(f"{base}/getnum", json={"rid": str(rng)}, headers={"mauthapi": api_key}, timeout=timeout)
        d = res.json()
        if d.get("meta", {}).get("code") == 200 and d.get("data"):
            return _digits_only(d["data"].get("no_plus_number") or d["data"].get("national_number"))
        return ""
    if label == "zenex":
        payload = {"range": _pad_range(rng), "is_national": False, "remove_plus": True}
        res = requests.post(f"{ZENEX_BASE_URL}/v1/getnum", json=payload, headers={"mapikey": api_key}, timeout=timeout)
        d = res.json()
        if d.get("meta", {}).get("code") == 200 and d.get("data"):
            return _digits_only(d["data"].get("full_number") or d["data"].get("number"))
        safe_print(f"zenex getnum rejected: {str(d)[:200]}")
        return ""
    if label == "mino":
        payload = {"api_key": api_key, "rid": _pad_range(rng), "national_format": 0, "remove_plus": 1}
        res = requests.post(f"{MINO_BASE_URL}/getnumber", json=payload, timeout=timeout)
        d = res.json()
        num = _find_number_in(d)
        if not num:
            safe_print(f"mino getnumber rejected: {str(d)[:200]}")
        return num
    return ""

def fetch_numbers_from_api(query, chat_id, prefer_voltx=False, req_count=None, prefer=None):
    """Try Stex/Voltx/Zenex/Mino. Preferred provider first. Short timeouts so UI never hangs."""
    if req_count is None:
        req_count = bot_settings.get("num_req", 1)
    req_count = max(1, min(int(req_count or 1), 3))
    fetched = []
    source = None
    timeout = 6

    if prefer is None:
        prefer = "voltx" if prefer_voltx else "stex"
    order = [prefer] + [l for l in API_PROVIDERS if l != prefer]

    for label in order:
        keys = provider_keys(label)
        if not keys:
            continue
        for _ in range(max(1, req_count - len(fetched))):
            if len(fetched) >= req_count:
                break
            got = False
            for api_key in keys[:3]:
                try:
                    num_str = _request_number(label, api_key, query, timeout)
                except Exception as e:
                    safe_print(f"{label} getnum error: {e}")
                    continue
                if num_str and num_str not in fetched:
                    fetched.append(num_str)
                    provider_assigned(label)[num_str] = chat_id
                    source = source or label
                    got = True
                    break
            if not got:
                break
        if len(fetched) >= req_count:
            break

    return fetched, source

def take_local_numbers(service, country, chat_id):
    """Atomically find + assign local numbers under a lock (fixes race / empty assign)."""
    global total_assigned_stats
    with stock_lock:
        indices = find_local_stock_indices(service, country, chat_id)
        if not indices:
            return []

        req = max(1, int(bot_settings.get("num_req", 1) or 1))
        share_limit = max(1, int(bot_settings.get("num_share", 1) or 1))
        random.shuffle(indices)
        fetched_nums = []
        taken_keys = set()  # (b_id, num) avoid double-take

        for b_id, idx in indices:
            if len(fetched_nums) >= req:
                break
            batch = number_batches.get(b_id)
            if not batch:
                continue
            nums = batch.get("numbers") or []
            # Re-resolve by scanning (index may be stale under concurrency)
            pick = None
            pick_i = None
            if 0 <= idx < len(nums) and isinstance(nums[idx], dict) and nums[idx].get("num"):
                cand = nums[idx]
                key = (b_id, str(cand.get("num")))
                if key not in taken_keys and not user_already_used_number(cand, chat_id):
                    pick, pick_i = cand, idx
            if pick is None:
                for i, cand in enumerate(nums):
                    if not isinstance(cand, dict) or not cand.get("num"):
                        continue
                    key = (b_id, str(cand.get("num")))
                    if key in taken_keys or user_already_used_number(cand, chat_id):
                        continue
                    pick, pick_i = cand, i
                    break
            if pick is None:
                continue

            num_str = str(pick["num"])
            taken_keys.add((b_id, num_str))
            fetched_nums.append(num_str)
            pick["shares"] = int(pick.get("shares", 0) or 0) + 1
            pick.setdefault("used_by", []).append(int(chat_id) if str(chat_id).isdigit() else chat_id)
            total_assigned_stats += 1
            if pick["shares"] >= share_limit:
                pick["to_remove"] = True
                used_numbers_list.append(num_str)

        for b_id in list(number_batches.keys()):
            number_batches[b_id]["numbers"] = [
                n for n in number_batches[b_id].get("numbers", [])
                if not (isinstance(n, dict) and n.get("to_remove"))
            ]
        try:
            save_local_db()
        except Exception as e:
            safe_print(f"save_local_db after assign error: {e}")
        return fetched_nums

def build_number_result_keyboard(service, country, fetched_nums, change_cb):
    """Original fancy keyboard: premium app/flag emoji, copy_text, OTP Group, custom buttons."""
    app_full_name, _ = get_service_info_html(service or "Number")
    emoji_id = "5337302974806922068"
    for app_key, app_data in bot_settings.get("premium_apps", {}).items():
        su = str(service or "").upper()
        if su == app_key or su in app_key or app_key in su:
            if app_data.get("id"):
                emoji_id = app_data["id"]
                break

    kb = [[{"text": f"{app_full_name}", "icon_custom_emoji_id": emoji_id, "callback_data": "ignore", "style": "success"}]]

    flags_db = bot_settings.get("premium_flags", {})
    for num in fetched_nums:
        _, iso = get_flag_and_code(num)
        display_num = f"+{num}" if not str(num).startswith("+") else str(num)
        flag_eid = "5780471598922337683"
        for flag_data in flags_db.values():
            if iso == flag_data.get("iso") and flag_data.get("id"):
                flag_eid = flag_data["id"]
                break
        kb.append([{
            "text": display_num,
            "icon_custom_emoji_id": flag_eid,
            "copy_text": {"text": display_num},
            "style": "primary",
        }])

    action_row = [{
        "text": "Change Number",
        "icon_custom_emoji_id": "5465368548702446780",
        "callback_data": str(change_cb)[:64],
        "style": "danger",
    }]
    otp_link = str(bot_settings.get("otp_link") or "").strip()
    if otp_link.startswith("http"):
        action_row.append({
            "text": "OTP Group",
            "icon_custom_emoji_id": "5190447043545438788",
            "url": otp_link,
            "style": "primary",
        })
    kb.append(action_row)

    for c_b in bot_settings.get("custom_messages", {}).get("get_number", {}).get("buttons", []):
        if c_b.get("enabled", True):
            b_copy = c_b.copy()
            if "style" not in b_copy:
                b_copy["style"] = "primary"
            kb.append([b_copy])

    kb.append([{
        "text": "Close",
        "icon_custom_emoji_id": "5420130255174145507",
        "callback_data": "close_msg",
        "style": "danger",
    }])
    return {"inline_keyboard": kb}

def deliver_assigned_numbers(chat_id, msg_id, service, country, fetched_nums, change_cb):
    """Deliver numbers ONLY as buttons (premium emoji + copy_text). No text body."""
    markup = build_number_result_keyboard(service, country, fetched_nums, change_cb)

    body_txt = build_assigned_text(fetched_nums)
    res = edit_blank_keyboard(chat_id, msg_id, markup, body_txt)
    if res and res.get("ok"):
        user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": list(fetched_nums)}
        return True

    safe_print(f"edit_message failed delivering keyboard: {res}")
    msg_res = send_blank_keyboard(chat_id, markup, body_txt)
    if msg_res and msg_res.get("ok") and "result" in msg_res:
        user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": list(fetched_nums)}
        try:
            delete_message(chat_id, msg_id)  # remove stale "Processing..." message
        except Exception:
            pass
        return True

    # Telegram rejected the fancy keyboard entirely -> plain keyboard (numbers still only on buttons)
    plain_kb = []
    for num in fetched_nums:
        display = str(num) if str(num).startswith("+") else f"+{num}"
        plain_kb.append([{"text": display, "copy_text": {"text": display}}])
    plain_kb.append([{"text": "Change Number", "callback_data": str(change_cb)[:64]},
                     {"text": "Close", "callback_data": "close_msg"}])
    plain = {"inline_keyboard": plain_kb}
    res = edit_blank_keyboard(chat_id, msg_id, plain, body_txt)
    if res and res.get("ok"):
        user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": list(fetched_nums)}
        return True
    msg_res = send_blank_keyboard(chat_id, plain, body_txt)
    if msg_res and msg_res.get("ok") and "result" in msg_res:
        user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": list(fetched_nums)}
        try:
            delete_message(chat_id, msg_id)
        except Exception:
            pass
        return True
    user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": list(fetched_nums)}
    return False

# ==========================================
# Callback Query Handler
# ==========================================
def handle_callback(call):
    global total_assigned_stats, users_db, withdrawals_db
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")
    callback_id = call.get("id", "")

    # ALWAYS clear Telegram loading spinner first (except when we need alert text below)
    early_answer = not (
        data.startswith("wapp_") or data.startswith("wrej_") or data == "check_fj"
        or data.startswith("test_p_conn_")
    )
    if early_answer and callback_id and callback_id != "internal":
        try:
            threading.Thread(target=answer_callback, args=(callback_id,), daemon=True).start()
        except Exception:
            pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    msg_id = call["message"]["message_id"]

    if chat_type == "private":
        if is_user_banned(chat_id):
            if callback_id and callback_id != "internal":
                answer_callback(callback_id, "🚫 You are banned from using this bot!", show_alert=True)
            return

        if not check_force_join(chat_id) and data != "check_fj":
            if callback_id and callback_id != "internal":
                try:
                    answer_callback(callback_id, "⚠️ Please join required channels first!", show_alert=True)
                except Exception:
                    pass
            send_force_join_msg(chat_id)
            return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Thanks for joining! You can now use the bot."), reply_markup=main_menu(chat_id))
            
            uid_str = str(chat_id)
            if uid_str in users_db:
                u_data = users_db[uid_str]
                if u_data.get("referred_by") and not u_data.get("ref_paid"):
                    inviter = u_data["referred_by"]
                    u_data["ref_paid"] = True
                    users_db[uid_str] = u_data
                    
                    reward = bot_settings.get("refer_reward", 0.2)
                    update_balance(inviter, reward)
                    
                    inv_uid_str = str(inviter)
                    if inv_uid_str in users_db:
                        users_db[inv_uid_str]["total_refers"] = users_db[inv_uid_str].get("total_refers", 0) + 1
                        
                    save_db()
                    ref_msg = (
                        f"{PEM['gift']} <b>New Referral !</b>\n"
                        f"------------------\n"
                        f"🔥 <b>You Received {reward} TK</b>\n"
                        f"------------------\n"
                        f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                    )
                    send_message(inviter, render_body_text(ref_msg))
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels yet!", show_alert=True)
        return

    if data == "close_msg":
        delete_message(chat_id, msg_id)
        
    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        delete_message(chat_id, msg_id)

    elif data == "cancel_2fa":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "gen_2fa":
        user_states[chat_id] = "wait_for_2fa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            
            success_txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"《 🔐 <b>2FA CODE</b> 》\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                f"━━━━━━━━━━━━━━━"
            )
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except:
            answer_callback(call["id"], "❌ Error refreshing code!", show_alert=True)

    elif data == "cancel_snz_edit":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>SNZ CONTROL PANEL</b>"), reply_markup=snz_control_keyboard())

    # ==========================================
    # Button Management Callback Handlers
    # ==========================================
    elif data == "manage_btn_layout":
        edit_message(chat_id, msg_id, render_body_text("🎮 <b>Button Management Panel</b>\n\nConfigure visibility and positions of Main Menu Keyboard buttons below:"), reply_markup=button_mgmt_keyboard())
        
    elif data == "btn_mgmt_status":
        edit_message(chat_id, msg_id, render_body_text("🟢 <b>Button On/Off Settings</b>\n\nClick on any button to toggle its visibility/active state on the main keyboard:"), reply_markup=button_status_keyboard())
        
    elif data == "btn_mgmt_rearrange":
        edit_message(chat_id, msg_id, render_body_text("🔄 <b>Rearrange Keyboard Buttons</b>\n\nSelect a button to change its position (Up, Down, Left, Right or create new rows):"), reply_markup=button_rearrange_list_keyboard())
        
    elif data.startswith("btn_toggle_status_"):
        target_text = data.replace("btn_toggle_status_", "")
        found = False
        for row in bot_settings.get("main_keyboard_layout", []):
            for btn in row:
                if btn["text"] == target_text:
                    btn["enabled"] = not btn.get("enabled", True)
                    found = True
                    break
        if found:
            save_db()
            answer_callback(call["id"], f"Visibility of '{target_text}' updated!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🟢 <b>Button On/Off Settings</b>\n\nClick on any button to toggle its visibility/active state on the main keyboard:"), reply_markup=button_status_keyboard())

    elif data.startswith("btn_select_move_"):
        target_text = data.replace("btn_select_move_", "")
        edit_message(chat_id, msg_id, render_body_text(f"🚀 <b>Moving Button:</b> <code>{target_text}</code>\n\nReposition the button using control keys below:"), reply_markup=button_movement_keyboard(target_text))

    elif data.startswith("btn_move_left_"):
        target_text = data.replace("btn_move_left_", "")
        r, c = find_btn_in_layout(target_text)
        if r is not None and c > 0:
            layout = bot_settings["main_keyboard_layout"]
            layout[r][c], layout[r][c-1] = layout[r][c-1], layout[r][c]
            save_db()
            answer_callback(call["id"], "Moved Left ⬅️")
            edit_message(chat_id, msg_id, render_body_text(f"🚀 <b>Moving Button:</b> <code>{target_text}</code>\n\nReposition the button using control keys below:"), reply_markup=button_movement_keyboard(target_text))
        else:
            answer_callback(call["id"], "Cannot move further Left!", show_alert=True)

    elif data.startswith("btn_move_right_"):
        target_text = data.replace("btn_move_right_", "")
        r, c = find_btn_in_layout(target_text)
        if r is not None:
            layout = bot_settings["main_keyboard_layout"]
            if c < len(layout[r]) - 1:
                layout[r][c], layout[r][c+1] = layout[r][c+1], layout[r][c]
                save_db()
                answer_callback(call["id"], "Moved Right ➡️")
                edit_message(chat_id, msg_id, render_body_text(f"🚀 <b>Moving Button:</b> <code>{target_text}</code>\n\nReposition the button using control keys below:"), reply_markup=button_movement_keyboard(target_text))
            else:
                answer_callback(call["id"], "Cannot move further Right!", show_alert=True)

    elif data.startswith("btn_move_up_"):
        target_text = data.replace("btn_move_up_", "")
        r, c = find_btn_in_layout(target_text)
        if r is not None and r > 0:
            layout = bot_settings["main_keyboard_layout"]
            btn = layout[r].pop(c)
            layout[r-1].append(btn)
            if not layout[r]:
                layout.pop(r)
            save_db()
            answer_callback(call["id"], "Moved Up ⬆️")
            edit_message(chat_id, msg_id, render_body_text(f"🚀 <b>Moving Button:</b> <code>{target_text}</code>\n\nReposition the button using control keys below:"), reply_markup=button_movement_keyboard(target_text))
        else:
            answer_callback(call["id"], "Cannot move further Up!", show_alert=True)

    elif data.startswith("btn_move_down_"):
        target_text = data.replace("btn_move_down_", "")
        r, c = find_btn_in_layout(target_text)
        if r is not None:
            layout = bot_settings["main_keyboard_layout"]
            if r < len(layout) - 1:
                btn = layout[r].pop(c)
                layout[r+1].append(btn)
                if not layout[r]:
                    layout.pop(r)
                save_db()
                answer_callback(call["id"], "Moved Down ⬇️")
                edit_message(chat_id, msg_id, render_body_text(f"🚀 <b>Moving Button:</b> <code>{target_text}</code>\n\nReposition the button using control keys below:"), reply_markup=button_movement_keyboard(target_text))
            else:
                answer_callback(call["id"], "Cannot move further Down!", show_alert=True)

    elif data.startswith("btn_new_row_above_"):
        target_text = data.replace("btn_new_row_above_", "")
        r, c = find_btn_in_layout(target_text)
        if r is not None:
            layout = bot_settings["main_keyboard_layout"]
            btn = layout[r].pop(c)
            layout.insert(r, [btn])
            if r+1 < len(layout) and not layout[r+1]:
                layout.pop(r+1)
            save_db()
            answer_callback(call["id"], "New Row Created Above ➕")
            edit_message(chat_id, msg_id, render_body_text(f"🚀 <b>Moving Button:</b> <code>{target_text}</code>\n\nReposition the button using control keys below:"), reply_markup=button_movement_keyboard(target_text))

    elif data.startswith("btn_new_row_below_"):
        target_text = data.replace("btn_new_row_below_", "")
        r, c = find_btn_in_layout(target_text)
        if r is not None:
            layout = bot_settings["main_keyboard_layout"]
            btn = layout[r].pop(c)
            layout.insert(r+1, [btn])
            if not layout[r]:
                layout.pop(r)
            save_db()
            answer_callback(call["id"], "New Row Created Below ➕")
            edit_message(chat_id, msg_id, render_body_text(f"🚀 <b>Moving Button:</b> <code>{target_text}</code>\n\nReposition the button using control keys below:"), reply_markup=button_movement_keyboard(target_text))

    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Traffic Refreshed!", show_alert=False)

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        country_stats = {}
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query):
                    iso = t.get("iso", "XX")
                    flag = t.get("flag", "🌍")
                    if iso not in country_stats:
                        country_stats[iso] = {"count": 0, "flag": flag}
                    country_stats[iso]["count"] += 1
        
        if not country_stats:
            answer_callback(call["id"], "❌ No recent traffic found for this service!", show_alert=True)
            return
            
        kb = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]
            c_name = iso
            emoji_id = "5780471598922337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    if "id" in fdata: emoji_id = fdata["id"]
                    break
            
            btn_text = f"{c_name} ({iso}) - {count} OTP"
            kb.append([{"text": btn_text, "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore Service: {prem_app_html} {app_full_name}</b>\n\nSelect a country to view available ranges:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]
        iso_query = parts[3]
        
        nums = []
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                    num = t.get("number", "").replace("+", "").strip()
                    if num: nums.append(num)
        
        if not nums:
            answer_callback(call["id"], "❌ No recent numbers found for this country!", show_alert=True)
            return
            
        known_ranges = set()
        for s_name, c_dict in bot_settings.get("stex_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list:
                    known_ranges.add(r)
                    
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r):
                    r_counts[r] += 1
                    matched = True
                    break
            if not matched:
                if len(num) >= 7: r_counts[num[:7]] += 1
                else: r_counts[num] += 1
                    
        r_list = r_counts.most_common(12)
        kb = []
        for r, count in r_list:
            kb.append([{"text": f"{r} ({count})", "icon_custom_emoji_id": "5352862640592949843", "copy_text": {"text": r}, "style": "primary"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges for {prem_app_html} {app_full_name} - {prem_flag_html} {iso_query}</b>\n\nClick on any range to copy it."), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())

    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Manage Balance:"), reply_markup=get_cancel_kb())
        
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Ban or Unban:"), reply_markup=get_cancel_kb())

    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to View Profile:"), reply_markup=get_cancel_kb())

    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Menu Design Editor</b>\n\nSelect a menu block to edit its Body Text and Inline Buttons. You can use Premium Emojis too!"), reply_markup=menu_design_list_keyboard())

    elif data == "md_reset_defaults":
        bot_settings["custom_messages"] = DEFAULT_CUSTOM_MESSAGES.copy()
        save_db()
        answer_callback(call["id"], "✅ Resetted to Premium Defaults!", show_alert=True)

    elif data.startswith("md_edit_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_edit_", "")
        cm_text = render_body_text(bot_settings["custom_messages"].get(key, {}).get("text", "..."))
        try: edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Editing: {key.upper()}</b>\n\nPreview of current Text:\n{cm_text}"), reply_markup=menu_edit_options_keyboard(key))
        except: pass

    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        user_states[chat_id] = "wait_for_menu_text"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Edit Body: {key.upper()}</b>\n\nSend the new text. You can use Premium Emojis directly here.\n(Use standard HTML like <b>bold</b>, <i>italic</i> for formatting)"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})

    elif data.startswith("md_btns_"):
        answer_callback(call["id"]) 
        if chat_id in user_states: del user_states[chat_id] 
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_btns_", "")
        try:
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except:
            pass

    elif data.startswith("md_addbtn_"):
        key = data.replace("md_addbtn_", "")
        user_states[chat_id] = "wait_for_menu_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"➕ <b>Add Button: {key.upper()}</b>\n\nSend custom button in this format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_btns_{key}", "style": "danger"}]]})

    elif data.startswith("md_togbtn_"):
        parts = data.split("_")
        key = parts[2]
        b_idx = int(parts[3])
        if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
            btn = bot_settings["custom_messages"][key]["buttons"][b_idx]
            btn["enabled"] = not btn.get("enabled", True)
            save_db()
            answer_callback(call["id"], f"Button turned {'ON' if btn['enabled'] else 'OFF'}!", show_alert=False)
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data.startswith("md_delbtn_"):
        parts = data.split("_")
        key = parts[2]
        b_idx = int(parts[3])
        if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
            del bot_settings["custom_messages"][key]["buttons"][b_idx]
            save_db()
            answer_callback(call["id"], "✅ Button Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        
        if bal < min_w:
            answer_callback(call["id"], f"❌ আপনার ব্যালেন্স অপর্যাপ্ত! মিনিমাম {min_w} ৳ প্রয়োজন।", show_alert=True)
            return
            
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Method: {method}\n💰 Available Balance: {bal} ৳\n\n📝 Enter the amount you want to withdraw (Min: {min_w} ৳):"), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send the Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>\n\nUpload your TXT files or manually add them below:"), reply_markup=emoji_settings_keyboard())

    elif data == "up_flags_txt":
        user_states[chat_id] = "wait_for_flag_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Flag Emojis</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "up_apps_txt":
        user_states[chat_id] = "wait_for_app_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Service Apps</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "add_single_emoji":
        user_states[chat_id] = "wait_for_emoji_extract"
        edit_message(chat_id, msg_id, render_body_text("📝 যেকোনো একটি Premium Emoji সেন্ড করুন (যেমন: 🇧🇩 বা 🚫):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "dl_flags_txt":
        content = ""
        for code, fdata in bot_settings.get("premium_flags", {}).items():
            content += f"({code}) ({fdata['iso']}) {fdata['name']} {fdata['char']} {{\"emoji\":\"{fdata['char']}\",\"id\":\"{fdata['id']}\"}}\n"
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content.encode('utf-8'))
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No Flag Emojis found!", show_alert=True)

    elif data == "del_all_flags":
        bot_settings["premium_flags"] = {}
        save_db()
        answer_callback(call["id"], "✅ All Premium Flags Deleted Successfully!", show_alert=True)

    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message you want to broadcast (Text, Photo, Video, File etc)."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the numbers in a <b>.txt</b> file."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "delete_files":
        kb = []
        for b_id, b_data in number_batches.items():
            kb.append([{"text": f"{b_data['filename']} ({len(b_data['numbers'])})", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a file to delete:" if len(kb) > 1 else f"{PEM['no']} No files found."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            del number_batches[b_id]
            save_db()
            answer_callback(call["id"], "✅ File deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_used":
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Total Used Numbers:</b> {len(used_numbers_list)}"), reply_markup=kb)

    elif data == "show_unused":
        unused_count = sum(len(b["numbers"]) for b in number_batches.values())
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Total Unused Numbers:</b> {unused_count}"), reply_markup=kb)

    elif data == "dl_used":
        if not used_numbers_list:
            answer_callback(call["id"], "❌ No used numbers found!", show_alert=True)
            return
        content = "\n".join(used_numbers_list).encode('utf-8')
        send_document(chat_id, "used_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "dl_unused":
        unused_list = [n["num"] for b in number_batches.values() for n in b["numbers"]]
        if not unused_list:
            answer_callback(call["id"], "❌ No unused numbers found!", show_alert=True)
            return
        content = "\n".join(unused_list).encode('utf-8')
        send_document(chat_id, "unused_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "lb_main":
        if not is_admin(chat_id):
            answer_callback(call["id"], "🚫 Admin only!", show_alert=True)
            return
        today = get_local_date()
        txt = (
            f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>DAILY LEADERBOARD</b> 》\n━━━━━━━━━━━━━━━\n"
            f"<i>Resets every day at 12:00 AM (UTC+6).</i>\n"
            f"📅 <b>Today:</b> {today}\n━━━━━━━━━━━━━━━"
        )
        kb = [
            [{"text": "Today's Top OTP", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_daily_otps", "style": "success"}],
            [{"text": "Top Referrers (All Time)", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP (All Time)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        if not is_admin(chat_id):
            answer_callback(call["id"], "🚫 Admin only!", show_alert=True)
            return
        check_daily_lb_reset()
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            res_txt = ""
            count = 1
            if sub == "top_refs":
                title, icon = "TOP 5 REFERRERS", PEM.get('user', '👥')
                sorted_users = sorted(users_db.values(), key=lambda x: x.get("total_refers", 0), reverse=True)[:5]
                for d in sorted_users:
                    if d.get("total_refers", 0) > 0:
                        p = "└" if count == len(sorted_users) else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={d['user_id']}'>{d['user_id']}</a> ➔ <b>{d.get('total_refers',0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "daily_otps":
                title, icon = f"TODAY'S TOP 10 OTP ({get_local_date()})", PEM.get('msg', '📩')
                sorted_users = sorted(users_db.values(), key=lambda x: x.get("daily_otps", 0), reverse=True)[:10]
                shown = [d for d in sorted_users if d.get("daily_otps", 0) > 0]
                for d in shown:
                    p = "└" if count == len(shown) else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={d['user_id']}'>{d['user_id']}</a> ➔ <b>{d.get('daily_otps',0)}</b>\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No OTPs received today yet.</i>\n"

            elif sub == "top_otps":
                title, icon = "TOP 5 OTP RECEIVERS (ALL TIME)", PEM.get('msg', '📩')
                sorted_users = sorted(users_db.values(), key=lambda x: x.get("total_otps", 0), reverse=True)[:5]
                for d in sorted_users:
                    if d.get("total_otps", 0) > 0:
                        p = "└" if count == len(sorted_users) else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={d['user_id']}'>{d['user_id']}</a> ➔ <b>{d.get('total_otps',0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, icon = "LAST 10 WITHDRAWALS", PEM.get('money', '💸')
                sorted_ws = sorted(withdrawals_db.values(), key=lambda x: x.get('timestamp_raw', 0), reverse=True)[:10]
                for d in sorted_ws:
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == len(sorted_ws) else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        
    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>\nManage advanced bot configurations below:"), reply_markup=system_settings_keyboard())

    elif data == "stex_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>Stex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your Stex API Keys below:"), reply_markup=stex_control_keyboard())

    elif data == "add_stex_key":
        user_states[chat_id] = "wait_for_add_stex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Stex API Key (e.g. stx_...):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}]]})

    elif data == "view_stex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("stex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_stx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Stex Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_stx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("stex_keys", [])):
            del bot_settings["stex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Stex Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_stex_keys", "id": call["id"]})

    elif data == "stex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_sc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_search_country":
        user_states[chat_id] = "wait_for_add_sc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Country Code (e.g. 880 or 92):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_search_country", "style": "danger"}]]})

    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("search_countries", [])):
            del bot_settings["search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Country Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "stex_search_country", "id": call["id"]})

    elif data == "manage_stex_srv":
        kb = []
        srvs = bot_settings.get("stex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"sx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "sx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📦 <b>Stex Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "sx_add_srv":
        user_states[chat_id] = "wait_sx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("sx_srv_"):
        srv = data.replace("sx_srv_", "")
        kb = []
        countries = bot_settings["stex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"sx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"sx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"sx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_stex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("sx_add_cnt_"):
        srv = data.replace("sx_add_cnt_", "")
        user_states[chat_id] = "wait_sx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("sx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["stex_services"][srv].get(cnt, [])
        
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"sx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"sx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"sx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"sx_srv_{srv}", "style": "primary"}])
        
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("sx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_sx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 88017):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"sx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("sx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["stex_services"].get(srv, {}).get(cnt, []):
            bot_settings["stex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"sx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("sx_del_srv_"):
        srv = data.replace("sx_del_srv_", "")
        if srv in bot_settings["stex_services"]: del bot_settings["stex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_stex_srv", "id": call["id"]})

    elif data.startswith("sx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["stex_services"].get(srv, {}): del bot_settings["stex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"sx_srv_{srv}", "id": call["id"]})

    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())

    elif data == "add_voltx_key":
        user_states[chat_id] = "wait_for_add_voltx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Voltx API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})

    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Voltx Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["voltx_keys"]):
            del bot_settings["voltx_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_voltx_keys", "id": call["id"]})

    elif data == "voltx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("voltx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Voltx Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Voltx Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_voltx_search_country":
        user_states[chat_id] = "wait_for_add_vsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Voltx Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})

    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["voltx_search_countries"]):
            del bot_settings["voltx_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": call["id"]})

    elif data == "manage_voltx_srv":
        kb = []
        srvs = bot_settings.get("voltx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Voltx Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "vx_add_srv":
        user_states[chat_id] = "wait_vx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_voltx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_add_cnt_"):
        srv = data.replace("vx_add_cnt_", "")
        user_states[chat_id] = "wait_vx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["voltx_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("vx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["voltx_services"].get(srv, {}).get(cnt, []):
            bot_settings["voltx_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("vx_del_srv_"):
        srv = data.replace("vx_del_srv_", "")
        if srv in bot_settings["voltx_services"]: del bot_settings["voltx_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": call["id"]})

    elif data.startswith("vx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["voltx_services"].get(srv, {}): del bot_settings["voltx_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": call["id"]})

    elif data == "zenex_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())

    elif data == "add_zenex_key":
        user_states[chat_id] = "wait_for_add_zenex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Zenex API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}]]})

    elif data == "view_zenex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("zenex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_ztx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Zenex Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_ztx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["zenex_keys"]):
            del bot_settings["zenex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_zenex_keys", "id": call["id"]})

    elif data == "zenex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("zenex_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_zsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_zenex_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Zenex Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Zenex Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_zenex_search_country":
        user_states[chat_id] = "wait_for_add_zsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Zenex Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_search_country", "style": "danger"}]]})

    elif data.startswith("del_zsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["zenex_search_countries"]):
            del bot_settings["zenex_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "zenex_search_country", "id": call["id"]})

    elif data == "manage_zenex_srv":
        kb = []
        srvs = bot_settings.get("zenex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "zx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Zenex Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "zx_add_srv":
        user_states[chat_id] = "wait_zx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_srv_"):
        srv = data.replace("zx_srv_", "")
        kb = []
        countries = bot_settings["zenex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"zx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"zx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_zenex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_add_cnt_"):
        srv = data.replace("zx_add_cnt_", "")
        user_states[chat_id] = "wait_zx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["zenex_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"zx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"zx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_zx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("zx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["zenex_services"].get(srv, {}).get(cnt, []):
            bot_settings["zenex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("zx_del_srv_"):
        srv = data.replace("zx_del_srv_", "")
        if srv in bot_settings["zenex_services"]: del bot_settings["zenex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_zenex_srv", "id": call["id"]})

    elif data.startswith("zx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["zenex_services"].get(srv, {}): del bot_settings["zenex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_srv_{srv}", "id": call["id"]})

    elif data == "mino_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Mino Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('mino_keys', []))}\nManage your Mino API Keys below:"), reply_markup=mino_control_keyboard())

    elif data == "add_mino_key":
        user_states[chat_id] = "wait_for_add_mino_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Mino API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "mino_control", "style": "danger"}]]})

    elif data == "view_mino_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("mino_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_mtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "mino_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Mino Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_mtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["mino_keys"]):
            del bot_settings["mino_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Mino Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_mino_keys", "id": call["id"]})

    elif data == "mino_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("mino_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_msc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_mino_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "mino_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Mino Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Mino Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_mino_search_country":
        user_states[chat_id] = "wait_for_add_msc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Mino Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "mino_search_country", "style": "danger"}]]})

    elif data.startswith("del_msc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["mino_search_countries"]):
            del bot_settings["mino_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Mino Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "mino_search_country", "id": call["id"]})

    elif data == "manage_mino_srv":
        kb = []
        srvs = bot_settings.get("mino_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"mn_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "mn_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "mino_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Mino Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "mn_add_srv":
        user_states[chat_id] = "wait_mn_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("mn_srv_"):
        srv = data.replace("mn_srv_", "")
        kb = []
        countries = bot_settings["mino_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"mn_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"mn_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"mn_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_mino_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("mn_add_cnt_"):
        srv = data.replace("mn_add_cnt_", "")
        user_states[chat_id] = "wait_mn_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("mn_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["mino_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"mn_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"mn_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"mn_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"mn_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("mn_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_mn_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"mn_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("mn_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["mino_services"].get(srv, {}).get(cnt, []):
            bot_settings["mino_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"mn_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("mn_del_srv_"):
        srv = data.replace("mn_del_srv_", "")
        if srv in bot_settings["mino_services"]: del bot_settings["mino_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_mino_srv", "id": call["id"]})

    elif data.startswith("mn_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["mino_services"].get(srv, {}): del bot_settings["mino_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"mn_srv_{srv}", "id": call["id"]})

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Channel Username or Invite Link:\n<i>(Note: For private channels, use the numeric ID like -100...)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})

    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            del bot_settings["fj_channels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Channel deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "add_adm":
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID of the new Admin:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})

    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]
            save_db()
            answer_callback(call["id"], "✅ Admin deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Group ID/Username to forward messages to:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_id}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Custom Inline Button format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})

    elif data.startswith("del_fwbtn_"):
        parts = data.split("_")
        idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                save_db()
                answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]
            save_db()
            answer_callback(call["id"], "✅ Group deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        p_list = bot_settings["panels"]
        text = f"{PEM['gear']} <b>Panel Management</b>\n\n👀 <b>Panels:</b> {len(p_list)}\n\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            is_cr = is_cr_api_panel(p)
            if is_cr:
                conf = f"{PEM['ok']} {p.get('login_status', 'CR API')}"
            else:
                curl_cfg = get_panel_curl_config(p)
                conf = f"{PEM['ok']} {p.get('login_status', 'OK')}" if curl_cfg else f"{PEM['no']} No Curl"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panels_list_keyboard())

    elif data == "add_panel":
        user_states[chat_id] = "wait_for_add_panel"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text(
            "📋 <b>Add / Update Panel</b>\n\n"
            "Paste curl from browser DevTools (Copy as cURL).\n"
            "Must include <code>-b PHPSESSID=...</code>\n\n"
            "💾 Saved to <code>phpsseid.json</code> by URL.\n"
            "• <b>New URL</b> → panel auto-added\n"
            "• <b>Same URL</b> → PHPSESSID updated"
        ), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "danger"}]]})

    elif data.startswith("upd_curl_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_panel"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text(
            "📋 <b>Update Curl / PHPSESSID</b>\n\n"
            "Paste curl from browser DevTools.\n"
            "Same URL → only PHPSESSID replaced."
        ), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data == "list_del_panels":
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Select a Panel to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(bot_settings["panels"]):
            delete_panel_curl_config(bot_settings["panels"][idx])
            del bot_settings["panels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Panel deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_panels", "id": "internal"})

    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            p["status"] = "ON" if p["status"] == "OFF" else "OFF"
            save_db()
            edit_message(chat_id, msg_id, render_body_text(panel_config_text(p)), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            edit_message(chat_id, msg_id, render_body_text(panel_config_text(p)), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection. Please wait..."))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])

        try:
            is_cr = is_cr_api_panel(p)
            if not is_cr and not get_panel_curl_config(p):
                if wait_msg_id: delete_message(chat_id, wait_msg_id)
                send_message(chat_id, render_body_text("❌ <b>No Curl Config!</b>\nUse <b>Add Panel</b> or <b>Update Curl</b> and paste curl with PHPSESSID."))
                return
            try:
                parsed, raw_text = fetch_panel_otps(p)
            except Exception as e:
                if wait_msg_id: delete_message(chat_id, wait_msg_id)
                send_message(chat_id, render_body_text(f"❌ <b>Fetch Failed!</b>\nReason: {py_html.escape(str(e))}"))
                return

            if wait_msg_id: delete_message(chat_id, wait_msg_id)

            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n🎯 <b>Parsed Data Sample (Max 3):</b>\n\n"
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']
                    msg_txt = sample['message']
                    otp = sample['otp']
                    app_name = resolve_otp_service(sample.get("cli"), msg_txt, p.get("name"))
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg_txt)
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 Number: <code>{num}</code>\n"
                    txt += f"📝 Full Msg: <code>{py_html.escape(msg_txt)}</code>\n"
                    txt += f"🔐 OTP: <code>{otp}</code>\n"
                    txt += "➖" * 12 + "\n"
                send_message(chat_id, render_body_text(txt))
            else:
                safe_html = py_html.escape(str(raw_text)[:300])
                send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but couldn't parse OTP data.</b>\n\nRaw excerpt:\n<code>{safe_html}...</code>"))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Connection Failed!</b>\nError: {py_html.escape(str(e))}"))

    elif data == "snz_control":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>SNZ CONTROL PANEL</b>"), reply_markup=snz_control_keyboard())

    elif data == "snz_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>SNZ CONTROL PANEL</b>"), reply_markup=snz_control_keyboard())

    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the name of the new Withdrawal Method:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})

    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]
            save_db()
            answer_callback(call["id"], "✅ Method deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data.startswith("snz_"):
        key = data.replace("snz_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link", "w_group": "w_group"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_snz"
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_snz_edit", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"📝 Please send the new value for <code>{key_map[key]}</code>:"), reply_markup=cancel_kb)
            answer_callback(call["id"])

    elif data.startswith("g_s_"):
        service = data.split("g_s_")[1]
        svc_u = service.upper().strip()
        local_cnts = set()
        for b in number_batches.values():
            if str(b.get("service", "")).upper().strip() == svc_u and b.get("numbers"):
                local_cnts.add(b["country"])
        stex_cnts = set()
        for srv, countries in bot_settings.get("stex_services", {}).items():
            if str(srv).upper().strip() == svc_u:
                stex_cnts.update(countries.keys())
        voltx_cnts = set()
        for srv, countries in bot_settings.get("voltx_services", {}).items():
            if str(srv).upper().strip() == svc_u:
                voltx_cnts.update(countries.keys())
        extra_cnts = set()
        for _lbl in ("zenex", "mino"):
            for srv, countries in provider_services(_lbl).items():
                if str(srv).upper().strip() == svc_u:
                    extra_cnts.update(countries.keys())
        all_countries = local_cnts.union(stex_cnts).union(voltx_cnts).union(extra_cnts)
        
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        raw_txt = c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service)
        txt = render_body_text(raw_txt)
        
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in sorted(all_countries, key=lambda x: str(x).upper()):
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_c_{service}_{c}", "style": "success"}])
        
        for b in c_msg.get("buttons", []): 
            if b.get("enabled", True):
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "close_msg", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_c_") or data.startswith("c_n_"):
        try:
            now = time.time()
            if now - user_cooldowns.get(chat_id, 0) < float(bot_settings.get("cooldown", 0) or 0):
                left = int(bot_settings.get("cooldown", 0) - (now - user_cooldowns.get(chat_id, 0)))
                answer_callback(call["id"], f"⌛ Please wait {max(left, 1)}s.", show_alert=True)
                return

            user_cooldowns[chat_id] = now
            expire_previous_number(chat_id)

            if data.startswith("c_n_s_"):
                clean_data, req_provider = split_provider_suffix(data)
                parts_s = clean_data.split("_", 4)
                query = parts_s[3] if len(parts_s) > 3 else ""
                service_from_cb = parts_s[4] if len(parts_s) > 4 else None

                allowed_provs = allowed_providers_for_query(query)

                if not req_provider and not allowed_provs:
                    edit_message(chat_id, msg_id, render_body_text("❌ This country code is not allowed!"), reply_markup={"inline_keyboard": [[{"text": "Close", "callback_data": "close_msg", "style": "danger"}]]})
                    return

                # Local numbers matching range first
                fetched_nums = []
                api_source = None
                with stock_lock:
                    found_indices = []
                    for b_id, b_data in number_batches.items():
                        for idx, n_obj in enumerate(b_data.get("numbers", [])):
                            if not isinstance(n_obj, dict):
                                continue
                            num_clean = str(n_obj.get("num", "")).replace("+", "")
                            if num_clean.startswith(str(query)) and not user_already_used_number(n_obj, chat_id):
                                found_indices.append((b_id, idx))
                    if found_indices:
                        req = max(1, int(bot_settings.get("num_req", 1) or 1))
                        share_limit = max(1, int(bot_settings.get("num_share", 1) or 1))
                        random.shuffle(found_indices)
                        for b_id, idx in found_indices:
                            if len(fetched_nums) >= req:
                                break
                            batch = number_batches.get(b_id)
                            if not batch or idx >= len(batch.get("numbers", [])):
                                continue
                            n_obj = batch["numbers"][idx]
                            if not isinstance(n_obj, dict) or user_already_used_number(n_obj, chat_id):
                                continue
                            num_str = str(n_obj["num"])
                            fetched_nums.append(num_str)
                            n_obj["shares"] = int(n_obj.get("shares", 0) or 0) + 1
                            n_obj.setdefault("used_by", []).append(chat_id)
                            total_assigned_stats += 1
                            if n_obj["shares"] >= share_limit:
                                n_obj["to_remove"] = True
                                used_numbers_list.append(num_str)
                        for b_id in list(number_batches.keys()):
                            number_batches[b_id]["numbers"] = [
                                n for n in number_batches[b_id].get("numbers", [])
                                if not (isinstance(n, dict) and n.get("to_remove"))
                            ]
                        save_local_db()

                if not fetched_nums:
                    prefer_prov = req_provider or (allowed_provs[0] if allowed_provs else None)
                    fetched_nums, api_source = fetch_numbers_from_api(
                        query, chat_id, prefer=prefer_prov, req_count=bot_settings.get("num_req", 1)
                    )
                    if fetched_nums:
                        total_assigned_stats += len(fetched_nums)
                        save_local_db()

                if not fetched_nums:
                    edit_message(chat_id, msg_id, render_body_text("❌ <b>Number out of stock!</b>"), reply_markup={"inline_keyboard": [[{"text": "Close", "callback_data": "close_msg", "style": "danger"}]]})
                    return

                vtx_ext = PROVIDER_SUFFIX.get(api_source or req_provider, "")
                srv_ext = f"_{service_from_cb}" if service_from_cb else ""
                change_cb = f"c_n_s_{query}{srv_ext}{vtx_ext}"
                deliver_assigned_numbers(chat_id, msg_id, service_from_cb or "Number", query, fetched_nums, change_cb)
                safe_print(f"Assigned {len(fetched_nums)} via range {query} to {chat_id}")
                return

            # Normal GET NUMBER / Change Number
            prefix = "g_c_" if data.startswith("g_c_") else "c_n_"
            service, country = parse_service_country_callback(data, prefix)
            if not service or not country:
                edit_message(chat_id, msg_id, render_body_text("❌ Invalid service/country!"), reply_markup={"inline_keyboard": [[{"text": "Close", "callback_data": "close_msg", "style": "danger"}]]})
                return

            local_left = count_local_stock(service)
            safe_print(f"GET NUMBER user={chat_id} svc={service} cty={country} local={local_left} db={DB_FILE}")

            fetched_nums = take_local_numbers(service, country, chat_id)
            if fetched_nums:
                deliver_assigned_numbers(chat_id, msg_id, service, country, fetched_nums, f"c_n_{service}_{country}")
                safe_print(f"Assigned LOCAL {len(fetched_nums)} to {chat_id} | remaining={count_local_stock(service)}")
                return

            # No local — optional API (never leave user on endless Processing)
            api_ranges = get_api_ranges_for(service, country)
            prefer_prov = None
            target_range = None
            for _prov in API_PROVIDERS:
                if api_ranges.get(_prov):
                    target_range = random.choice(api_ranges[_prov])
                    prefer_prov = _prov
                    break

            if not target_range:
                edit_message(
                    chat_id, msg_id,
                    render_body_text(
                        f"❌ <b>Out of stock</b>\n"
                        f"Service: <code>{py_html.escape(service)}</code>\n"
                        f"Country: <code>{py_html.escape(country)}</code>\n"
                        f"Local left: <b>{local_left}</b>\n"
                        f"DB: <code>{py_html.escape(os.path.basename(DB_FILE))}</code>"
                    ),
                    reply_markup={"inline_keyboard": [[{"text": "Close", "callback_data": "close_msg", "style": "danger"}]]},
                )
                return

            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            fetched_nums, api_source = fetch_numbers_from_api(
                target_range, chat_id, prefer=prefer_prov, req_count=bot_settings.get("num_req", 1)
            )
            if not fetched_nums:
                edit_message(
                    chat_id, msg_id,
                    render_body_text("❌ <b>Number out of stock!</b>"),
                    reply_markup={"inline_keyboard": [[{"text": "Close", "callback_data": "close_msg", "style": "danger"}]]},
                )
                return

            total_assigned_stats += len(fetched_nums)
            save_local_db()
            vtx_flag = PROVIDER_SUFFIX.get(api_source or prefer_prov, "_stex")
            deliver_assigned_numbers(chat_id, msg_id, service, country, fetched_nums, f"c_n_s_{target_range}_{service}{vtx_flag}")
            safe_print(f"Assigned API {len(fetched_nums)} to {chat_id} range={target_range}")
        except Exception as e:
            safe_print(f"GET NUMBER fatal error: {e}")
            try:
                edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {py_html.escape(str(e)[:200])}"), reply_markup={"inline_keyboard": [[{"text": "Close", "callback_data": "close_msg", "style": "danger"}]]})
            except Exception:
                send_message(chat_id, render_body_text(f"❌ Error getting number: {py_html.escape(str(e)[:200])}"))

    elif data.startswith("wapp_") or data.startswith("wrej_"):
        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Only Bot Admins can process withdrawals!", show_alert=True)
            return
            
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        
        if req_id in pending_withdrawals:
            req_data = pending_withdrawals[req_id]
            u_id, amt = req_data["user_id"], req_data["amount"]
            num = req_data["number"]
            full_name = req_data.get("full_name", u_id)
            
            if action == "APPROVE" and len(num) >= 7:
                masked_num = f"{num[:4]}❖SNZ❖{num[-3:]}"
            else:
                masked_num = num
            
            status_text = "APPROVED" if action == "APPROVE" else "REJECTED"
            emoji_icon_id = "5352694861990501856" if action == "APPROVE" else "5420130255174145507"
            new_text = f"🎙 <b>WITHDRAWAL {status_text}</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={u_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amt} TK\n🍏 <b>NUMBER:</b> <code>{masked_num}</code>\n🏦 <b>METHOD:</b> {req_data['method']}\n\n🧾 <b>REQ ID:</b> {req_id}\n👑 <b>PROCESSED BY ADMIN</b>"
            
            kb = {"inline_keyboard": [[{"text": status_text, "icon_custom_emoji_id": emoji_icon_id, "callback_data": "ignore", "style": "success" if action == "APPROVE" else "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(new_text), reply_markup=kb)
            
            if action == "REJECT":
                update_balance(u_id, amt) 
                send_message(u_id, render_body_text(f"❌ Your {amt} TK withdrawal request was rejected. Balance refunded."))
            else:
                send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} TK withdrawal request has been paid successfully!"))
            
            if req_id in withdrawals_db:
                withdrawals_db[req_id]["status"] = "approved" if action == "APPROVE" else "rejected"
                save_db()
                
            del pending_withdrawals[req_id]
        else:
            answer_callback(call["id"], "❌ Request already processed!", show_alert=True)

# ==========================================
# Polling Loops
# ==========================================
def stex_sms_listener():
    global processed_otps, recent_traffic, stex_assigned_numbers, users_db
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            for api_key in stex_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{STEX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = resolve_otp_service(None, msg_text, "Stex Service")
                                
                            unique_id = make_otp_unique_id(num, otp)
                            if (not is_otp_duplicate(unique_id)) and num:
                                mark_otp_processed(unique_id)
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                display_msg = build_group_otp_message(display_num, otp, msg_text, prem_app_html, app_full_name)
                                
                                forward_otp_to_groups(display_msg, otp, num=display_num)
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for stex_n, n_owner in stex_assigned_numbers.items():
                                        clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    inbox_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} {display_num} {lang}\n╚═══════════════╝")
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    reward = float(bot_settings.get("otp_reward", 0.0))
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                        inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    increment_user_otp_count(owner_id)
                                    save_db()
                except: pass
        except: pass
        time.sleep(5)

def voltx_sms_listener():
    global processed_otps, recent_traffic, voltx_assigned_numbers, users_db
    while True:
        try:
            voltx_keys = bot_settings.get("voltx_keys", [])
            for api_key in voltx_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{VOLTX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = resolve_otp_service(None, msg_text, "Voltx Service")
                                
                            unique_id = make_otp_unique_id(num, otp)
                            if (not is_otp_duplicate(unique_id)) and num:
                                mark_otp_processed(unique_id)
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                display_msg = build_group_otp_message(display_num, otp, msg_text, prem_app_html, app_full_name)
                                
                                forward_otp_to_groups(display_msg, otp, num=display_num)
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for voltx_n, n_owner in voltx_assigned_numbers.items():
                                        clean_vtx = str(voltx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_vtx == clean_api_num or (len(clean_vtx) >= 8 and clean_vtx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    inbox_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} {display_num} {lang}\n╚═══════════════╝")
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    reward = float(bot_settings.get("otp_reward", 0.0))
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                        inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    increment_user_otp_count(owner_id)
                                    save_db()
                except: pass
        except: pass
        time.sleep(5)

# ==========================================
# Zenex & Mino SMS listeners (shared OTP delivery)
# ==========================================
def _norm_phone(v):
    return re.sub(r"\D", "", str(v or ""))

def process_api_otp(label, num, msg_text, extra_id=""):
    """Forward OTP to groups + deliver to the user who owns the number."""
    global recent_traffic
    num = _norm_phone(num)
    if not num or not msg_text:
        return
    otp = extract_otp_code(msg_text) or "CODE"
    unique_id = make_otp_unique_id(num, otp)
    if is_otp_duplicate(unique_id):
        return
    mark_otp_processed(unique_id)

    app_name = resolve_otp_service(None, msg_text, f"{PROVIDER_NAMES.get(label, label)} Service")
    char, iso = get_flag_and_code(num)
    app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
    current_time = time.time()
    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
    recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
    save_local_db()

    display_num = f"+{num}"
    masked = mask_number(display_num)
    lang = detect_language(msg_text)
    display_msg = build_group_otp_message(display_num, otp, msg_text, prem_app_html, app_full_name)
    forward_otp_to_groups(display_msg, otp, num=display_num)

    def _match(a, b):
        return a == b or (len(a) >= 8 and len(b) >= 8 and a[-8:] == b[-8:])

    owner_id = None
    for uid, session_data in list(user_active_sessions.items()):
        if any(_match(_norm_phone(n), num) for n in session_data.get("nums", [])):
            owner_id = uid
            break
    if not owner_id:
        for n, n_owner in list(provider_assigned(label).items()):
            if _match(_norm_phone(n), num):
                owner_id = n_owner
                break
    if not owner_id:
        return

    inbox_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} {display_num} {lang}\n╚═══════════════╝")
    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
    reward = float(bot_settings.get("otp_reward", 0.0))
    if reward > 0:
        update_balance(owner_id, reward)
        inbox_kb.append([{"text": f"Added {reward} tk", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
    increment_user_otp_count(owner_id)
    save_db()

def zenex_fetch_otps(api_key):
    res = requests.get(f"{ZENEX_BASE_URL}/v1/numsuccess/info", headers={"mapikey": api_key}, timeout=10)
    d = res.json()
    items = ((d.get("data") or {}).get("otps")) or []
    return [(it.get("number"), it.get("otp") or it.get("message"), it.get("nid")) for it in items if isinstance(it, dict)]

def _find_list_of_dicts(obj, depth=0):
    if depth > 3:
        return []
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        for k in ("otps", "data", "results", "messages", "items", "records", "sms", "list"):
            if k in obj:
                r = _find_list_of_dicts(obj[k], depth + 1)
                if r:
                    return r
    return []

def mino_fetch_otps(api_key):
    res = requests.get(f"{MINO_BASE_URL}/success_otp", params={"api_key": api_key}, timeout=10)
    d = res.json()
    out = []
    for it in _find_list_of_dicts(d):
        num = next((it[k] for k in ("number", "phone_number", "phone", "msisdn", "num") if it.get(k)), "")
        txt = next((it[k] for k in ("message", "sms", "text", "body", "content", "msg", "otp", "code") if it.get(k)), "")
        out.append((num, txt, it.get("id") or it.get("otp_id")))
    return out

def generic_sms_listener(label, fetch_fn):
    while True:
        try:
            for api_key in list(provider_keys(label)):
                try:
                    for num, txt, extra in fetch_fn(api_key):
                        try:
                            process_api_otp(label, num, str(txt or ""), str(extra or ""))
                        except Exception as e:
                            safe_print(f"{label} otp process error: {e}")
                except Exception as e:
                    safe_print(f"{label} listener error: {e}")
        except Exception:
            pass
        time.sleep(4)

# ==========================================
# Main Execution Entry
# ==========================================
def main():
    global BOT_USERNAME
    if OWNER_ID not in bot_settings["admins"]:
        bot_settings["admins"].insert(0, OWNER_ID)
        save_local_db()
    for uid in users_db:
        if "daily_otps" not in users_db[uid]:
            users_db[uid]["daily_otps"] = 0
    if "daily_lb_date" not in bot_settings:
        bot_settings["daily_lb_date"] = get_local_date()
    check_daily_lb_reset()

    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")
    
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=stex_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    threading.Thread(target=generic_sms_listener, args=("zenex", zenex_fetch_otps), daemon=True).start()
    threading.Thread(target=generic_sms_listener, args=("mino", mino_fetch_otps), daemon=True).start()
    threading.Thread(target=daily_lb_reset_thread, daemon=True).start()
    print("📡 Background APIs & Global SMS Listener Started!")
    
    executor = ThreadPoolExecutor(max_workers=500)
    offset = None
    while True:
        try:
            updates = get_updates(offset=offset, timeout=50)
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update: 
                        executor.submit(handle_message, update["message"])
                    elif "callback_query" in update: 
                        executor.submit(handle_callback, update["callback_query"])
        except Exception as e:
            print(f"⚠️ Poll loop error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()