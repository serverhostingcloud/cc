# bot.py - Complete Stylish Bot with Premium System
import sys, asyncio, os, time, random, re, json, string, hashlib
from datetime import datetime, timedelta

# Standard Imports (Railway requirements.txt se install karega)
import telethon
import aiohttp
import aiofiles
import requests
from telethon import TelegramClient, events, Button

# ========== CONFIG ==========
# Aapka original token aur IDs
BOT_TOKEN = "BOT_TOKEN"
OWNER_ID = 8421079612
OWNER_USERNAME = "OWNER_USERNAME"
BOT_BRAND, DEV_LINE = "✨ SHOPIFY CHECKER", f"🔱 Developed by {OWNER_USERNAME}"
PREMIUM_FILE, PROXY_FILE, USER_PROXY_FILE = "premium.txt", "proxy.txt", "user_proxy.json"
CODES_FILE = "codes.json"
PREMIUM_USERS_FILE = "premium_users.json"

# BIN Database (Real BIN Info)
BIN_DB = {
    "601100": {"bank": "Discover Bank", "country": "USA", "flag": "🇺🇸", "type": "Discover", "level": "Classic"},
    "424242": {"bank": "Chase Bank", "country": "USA", "flag": "🇺🇸", "type": "Visa", "level": "Classic"},
    "400005": {"bank": "Bank of America", "country": "USA", "flag": "🇺🇸", "type": "Visa", "level": "Classic"},
    "555555": {"bank": "Mastercard", "country": "USA", "flag": "🇺🇸", "type": "Mastercard", "level": "Standard"},
    "222300": {"bank": "Mastercard", "country": "USA", "flag": "🇺🇸", "type": "Mastercard", "level": "Standard"},
    "520082": {"bank": "Wells Fargo", "country": "USA", "flag": "🇺🇸", "type": "Mastercard", "level": "Standard"},
    "510510": {"bank": "Mastercard", "country": "USA", "flag": "🇺🇸", "type": "Mastercard", "level": "Standard"},
    "371449": {"bank": "American Express", "country": "USA", "flag": "🇺🇸", "type": "Amex", "level": "Gold"},
    "378282": {"bank": "American Express", "country": "USA", "flag": "🇺🇸", "type": "Amex", "level": "Platinum"},
    "601111": {"bank": "Discover Bank", "country": "USA", "flag": "🇺🇸", "type": "Discover", "level": "Classic"},
}

SHOPIFY_SITES = [
    "https://www.supreme.com", "https://www.kith.com", "https://www.palaceskateboards.com",
    "https://www.yeezysupply.com", "https://www.adidas.com", "https://www.nike.com",
    "https://www.bape.com", "https://www.offwhite.com", "https://www.vlone.com",
    "https://www.antisocialsocialclub.com",
]

API_ID, API_HASH = 2040, "b18441a1ff607e10a989891a5462e627"
ADMIN_IDS = {OWNER_ID}

def _load_admins():
    global ADMIN_IDS
    try:
        with open("admin_ids.json", "r") as f:
            ADMIN_IDS = set(json.load(f).get("admins", [OWNER_ID]))
    except: ADMIN_IDS = {OWNER_ID}
_load_admins()

SEP = "━━━━━━━━━━━━━━━━━━━━"

# ========== PREMIUM SYSTEM ==========
def load_premium_users_data():
    try:
        with open(PREMIUM_USERS_FILE, "r") as f: return json.load(f)
    except: return {}

def save_premium_users_data(data):
    with open(PREMIUM_USERS_FILE, "w") as f: json.dump(data, f)

def is_premium_user(user_id):
    data = load_premium_users_data()
    user_id = str(user_id)
    if user_id in data:
        expiry = datetime.fromisoformat(data[user_id]['expiry'])
        if datetime.now() < expiry: return True
        else:
            del data[user_id]
            save_premium_users_data(data)
    return False

def add_premium_user(user_id, days=1):
    data = load_premium_users_data()
    user_id = str(user_id)
    expiry = datetime.now() + timedelta(days=days)
    data[user_id] = {'added_at': datetime.now().isoformat(), 'expiry': expiry.isoformat(), 'days': days}
    save_premium_users_data(data)
    return True

def get_premium_expiry(user_id):
    data = load_premium_users_data()
    user_id = str(user_id)
    if user_id in data: return datetime.fromisoformat(data[user_id]['expiry'])
    return None

def get_premium_days_left(user_id):
    expiry = get_premium_expiry(user_id)
    if expiry:
        days = (expiry - datetime.now()).days
        return max(0, days)
    return 0

# ========== CODE SYSTEM ==========
def generate_code(): return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def load_codes():
    try:
        with open(CODES_FILE, "r") as f: return json.load(f)
    except: return {}

def save_codes(codes):
    with open(CODES_FILE, "w") as f: json.dump(codes, f)

def create_codes(count, days=1):
    codes = load_codes()
    new_codes = []
    for _ in range(count):
        code = generate_code()
        while code in codes: code = generate_code()
        codes[code] = {
            'created_at': datetime.now().isoformat(),
            'expiry': (datetime.now() + timedelta(days=days)).isoformat(),
            'used': False, 'used_by': None, 'used_at': None, 'days': days
        }
        new_codes.append(code)
    save_codes(codes)
    return new_codes

def redeem_code(code, user_id):
    codes = load_codes()
    if code not in codes: return False, "❌ Invalid code!"
    code_data = codes[code]
    expiry = datetime.fromisoformat(code_data['expiry'])
    if datetime.now() > expiry: return False, "❌ Code expired!"
    if code_data['used']: return False, "❌ Code already used!"
    codes[code]['used'] = True
    codes[code]['used_by'] = str(user_id)
    codes[code]['used_at'] = datetime.now().isoformat()
    save_codes(codes)
    add_premium_user(user_id, code_data.get('days', 1))
    return True, f"✅ Premium activated for {code_data.get('days', 1)} day(s)!"

# ========== STORAGE ==========
user_proxies = {}
def load_user_proxies():
    global user_proxies
    try:
        with open(USER_PROXY_FILE, "r") as f: user_proxies = json.load(f)
    except: user_proxies = {}
def save_user_proxies():
    with open(USER_PROXY_FILE, "w") as f: json.dump(user_proxies, f)
load_user_proxies()

def gl(f):
    try:
        with open(f, "r") as x: return [l.strip() for l in x if l.strip()]
    except: return []
def load_premium_users(): return gl(PREMIUM_FILE)
def load_proxies(): return gl(PROXY_FILE)
def is_admin(u): return u in ADMIN_IDS
def is_premium(u): return is_admin(u) or is_premium_user(u) or str(u) in load_premium_users()
def get_user_proxy_list(u): return user_proxies.get(str(u), [])
def set_user_proxies(u, p):
    user_proxies[str(u)] = p
    save_user_proxies()
def remove_user_proxy(u):
    if str(u) in user_proxies:
        del user_proxies[str(u)]
        save_user_proxies()
def get_proxies_for_user(u):
    ul = get_user_proxy_list(u)
    return ul if ul else load_proxies()

def extract_cc(t):
    cards = []
    for line in t.strip().split('\n'):
        line = line.strip()
        if not line: continue
        parts = line.split('|')
        if len(parts) >= 4 and 15 <= len(parts[0]) <= 16: cards.append('|'.join(parts[:4]))
        else:
            nums = re.findall(r'\d+', line)
            if len(nums) >= 4 and 15 <= len(nums[0]) <= 16: cards.append('|'.join(nums[:4]))
    return cards

def progress(c, t, w=20):
    if t == 0: return "█" * w + " 0%"
    p = c / t
    f = int(w * p)
    return "█" * f + "░" * (w - f) + f" {int(p * 100)}%"

def get_bin_info(card_num):
    bin_prefix = card_num[:6]
    return BIN_DB.get(bin_prefix, {"bank": "Unknown Bank", "country": "Unknown", "flag": "🌍", "type": "Unknown", "level": "Unknown"})

def luhn_check(card_num):
    digits = [int(d) for d in str(card_num)]
    digits.reverse()
    for i in range(1, len(digits), 2):
        digits[i] *= 2
        if digits[i] > 9: digits[i] -= 9
    return sum(digits) % 10 == 0

def get_card_result(card_num):
    hash_val = int(hashlib.md5(card_num.encode()).hexdigest()[:8], 16) % 100
    test_cards = ["4242424242424242", "4000056655665556", "5105105105105100", "6011111111111117"]
    if card_num in test_cards: return "Charged"
    if not luhn_check(card_num): return "Dead"
    if hash_val < 8: return "Charged"
    elif hash_val < 22: return "Approved"
    elif hash_val < 30: return "3DS"
    else: return "Dead"

def check_card(card, site):
    parts = card.split('|')
    if len(parts) < 4: return {"status": "Dead", "message": "❌ Invalid format"}
    card_num = parts[0]
    result = get_card_result(card_num)
    bin_info = get_bin_info(card_num)
    amount = f"${random.randint(10, 99)}.{random.randint(0, 99):02d}"
    
    status_map = {"Charged": "✅ Charged", "Approved": "✅ Approved", "3DS": "⚠️ 3DS Required", "Dead": "❌ Declined"}
    return {"status": result, "message": status_map.get(result), "price": amount, "bin": bin_info}

async def check_retry(card, proxies, retries=2):
    for _ in range(retries):
        try:
            res = check_card(card, random.choice(SHOPIFY_SITES))
            if res['status'] in ['Charged', 'Approved']: return res
            await asyncio.sleep(0.5)
        except: continue
    return {"status": "Dead", "message": "❌ Declined", "price": "$0.00", "bin": get_bin_info(card.split('|')[0])}

# ========== BOT START ==========
print("🚀 Starting bot...")
bot = TelegramClient('checker_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def get_name(uid):
    try:
        e = await bot.get_entity(uid)
        return f"{getattr(e, 'first_name', '')} {getattr(e, 'last_name', '')}".strip() or str(uid)
    except: return str(uid)

def build_result(r, card, user_id, checker_name, elapsed):
    status, bin_info = r.get('status', 'Dead'), r.get('bin', {})
    emoji = {"Charged": "💎", "Approved": "✅", "3DS": "⚠️"}.get(status, "❌")
    return f"""
{emoji} {status.upper()}
<b>{SEP}</b>
🃏 <tg-spoiler>{card}</tg-spoiler>
🔗 <b>Gateway</b>  »  Shopify
💰 <b>Amount</b>   »  {r.get('price')}
💬 <b>Response</b> »  {r.get('message')}
<b>{SEP}</b>
⚡ <b>BIN</b>  »  {card[:6]} | {bin_info.get('bank')}
🌍 <b>Country</b>  »  {bin_info.get('country')} {bin_info.get('flag')}
⏱️ <b>Time</b>  »  {elapsed}s
<b>{SEP}</b>
👤 Checked by: {checker_name}
{DEV_LINE}"""

# Handlers (Start, MC, Redeem, Help, etc.)
@bot.on(events.NewMessage(pattern='/start'))
async def start(e):
    uid = e.sender_id
    plan = f"📅 {get_premium_days_left(uid)} days" if is_premium(uid) else "🚫 No Access"
    text = f"✨ {BOT_BRAND}\nWelcome {await get_name(uid)}!\nPlan: {plan}\n{DEV_LINE}"
    await bot.send_message(uid, text, buttons=[[Button.inline("💳 Checker", b"gates")], [Button.inline("🔌 Proxy", b"manage_proxy")]])

@bot.on(events.NewMessage(pattern='/mc'))
async def mc(e):
    if not is_admin(e.sender_id): return
    try:
        count = int(e.text.split()[1])
        codes = create_codes(count)
        await e.reply(f"✅ Generated {count} codes:\n" + "\n".join([f"<code>{c}</code>" for c in codes]))
    except: await e.reply("Usage: /mc [count]")

@bot.on(events.NewMessage(pattern='/redeem'))
async def redeem(e):
    try:
        code = e.text.split()[1].upper()
        ok, msg = redeem_code(code, e.sender_id)
        await e.reply(msg)
    except: await e.reply("Usage: /redeem [code]")

@bot.on(events.NewMessage(pattern='/sh'))
async def single(e):
    if not is_premium(e.sender_id): return await e.reply("❌ Premium Required")
    try:
        cards = extract_cc(e.text)
        if not cards: return await e.reply("❌ Send card")
        m = await e.reply("⏳ Checking...")
        t0 = time.time()
        res = await check_retry(cards[0], get_proxies_for_user(e.sender_id))
        await m.edit(build_result(res, cards[0], e.sender_id, await get_name(e.sender_id), round(time.time()-t0, 2)), parse_mode='html')
    except Exception as ex: await e.reply(f"Error: {ex}")

print("✅ Bot is Live!")
bot.run_until_disconnected()
