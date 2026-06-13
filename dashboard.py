import os
import logging
import aiohttp
from quart import Quart, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
from database import db_manager

load_dotenv()
logger = logging.getLogger("Bot.Dashboard")

app = Quart(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

app.bot = None 

# --- WEB UI STYLE CONSTANTS ---
GLOBAL_BODY_STYLE = "font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #23272a; color: #ffffff; padding: 40px; margin: 0;"
NAV_BANNER_URL = "https://media.discordapp.net/attachments/1503357008722530377/1505483556959293628/11.png"

@app.route("/")
async def home():
    return f"""
    <html>
        <head>
            <title>Ender Bot Portal</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="{GLOBAL_BODY_STYLE} text-align: center; padding-top: 120px;">
            <div style="max-width: 500px; margin: 0 auto; background: #2c2f33; padding: 40px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
                <img src="{NAV_BANNER_URL}" style="width: 100%; border-radius: 8px; margin-bottom: 25px;">
                <h1 style="margin-bottom: 30px; font-weight: 700; letter-spacing: 0.5px;">🤖 ENDER BOT v2.0 PORTAL</h1>
                <p style="color: #b9bbbe; margin-bottom: 35px;">Manage tickets, logging maps, automod structures, and system arrays seamlessly.</p>
                <a style="display: block; background: #5865F2; color: #ffffff; padding: 16px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; transition: background 0.2s;" href="/login">Log In With Discord</a>
            </div>
        </body>
    </html>
    """

@app.route("/login")
async def login():
    oauth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20guilds"
    return redirect(oauth_url)

@app.route("/callback")
async def callback():
    code = request.args.get("code")
    if not code: 
        return "Missing authorized callback identity token context", 400
        
    data = {
        'client_id': CLIENT_ID, 
        'client_secret': CLIENT_SECRET, 
        'grant_type': 'authorization_code', 
        'code': code, 
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    async with aiohttp.ClientSession() as session_client:
        async with session_client.post("https://discord.com/api/oauth2/token", data=data, headers=headers) as resp:
            token_json = await resp.json()
            if resp.status != 200: 
                return "OAuth execution token exchange sequence error.", 400
            session["discord_token"] = token_json.get("access_token")
            return redirect(url_for("user_dashboard"))

@app.route("/dashboard")
async def user_dashboard():
    token = session.get("discord_token")
    if not token: 
        return redirect(url_for("login"))
        
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session_client:
        async with session_client.get("https://discord.com/api/v10/users/@me", headers=headers) as u_resp:
            user_data = await u_resp.json()
        async with session_client.get("https://discord.com/api/v10/users/@me/guilds", headers=headers) as g_resp:
            all_guilds = await g_resp.json()

    if not isinstance(all_guilds, list):
        return "Failed to fetch servers listing from Discord gateway core.", 500

    bot_guild_ids = [guild.id for guild in app.bot.guilds] if (app.bot and app.bot.is_ready()) else []
    guilds_html = ""
    
    for g in all_guilds:
        if not (int(g.get("permissions", 0)) & 0x8 == 0x8): 
            continue
        guild_id = int(g["id"])
        guild_name = g["name"]
        icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{g.get('icon')}.png" if g.get('icon') else "https://cdn.discordapp.com/embed/avatars/0.png"
        
        if guild_id in bot_guild_ids:
            btn = f'<a href="/manage/{guild_id}" style="background:#43b581;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;font-weight:bold;font-size:14px;">Manage</a>'
        else:
            inv = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions=8&scope=bot%20applications.commands&guild_id={guild_id}&disable_guild_select=true"
            btn = f'<a href="{inv}" target="_blank" style="background:#5865F2;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;font-weight:bold;font-size:14px;">Invite</a>'
        
        guilds_html += f"""
        <div style="background:#2c2f33;padding:18px;border-radius:8px;display:flex;align-items:center;margin-bottom:12px;box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
            <img src="{icon_url}" style="width:52px;height:52px;border-radius:50%;margin-right:18px;object-fit:cover;">
            <div style="flex-grow:1;">
                <span style="font-weight:600;font-size:16px;letter-spacing:0.3px;">{guild_name}</span>
            </div>
            {btn}
        </div>
        """

    return f"""
    <html>
        <head>
            <title>Ender Bot Mainframe</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="{GLOBAL_BODY_STYLE}">
            <div style="max-width:800px;margin:0 auto;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:30px;border-bottom:2px solid #2c2f33;padding-bottom:20px;">
                    <h2 style="margin:0;font-weight:600;">Welcome, {user_data.get("username", "Admin")} 👋</h2>
                    <span style="background:#7289da;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:bold;letter-spacing:0.5px;">SYSTEM MAINBOARD</span>
                </div>
                <h3 style="color:#b9bbbe;margin-bottom:20px;font-size:14px;text-transform:uppercase;letter-spacing:1px;">Your Operational Environments</h3>
                {guilds_html if guilds_html else '<p style="color:#b9bbbe;">No servers located with valid Administrative permission configurations.</p>'}
            </div>
        </body>
    </html>
    """

@app.route("/manage/<int:guild_id>", methods=["GET"])
async def manage_server(guild_id):
    if not session.get("discord_token"): 
        return redirect(url_for("login"))
    if not app.bot: 
        return "Initializing runtime arrays...", 503
        
    guild = app.bot.get_guild(guild_id)
    if not guild: 
        return "Bot cache execution misaligned. Invite the framework first.", 404

    config_collection = db_manager.get_collection("guild_settings")
    settings = await config_collection.find_one({"guild_id": guild_id}) or {}
    
    automod_status = settings.get("automod_enabled", True)
    mod_cmds_status = settings.get("mod_cmds_enabled", True)
    logging_channel_id = settings.get("logging_channel_id", "") or ""
    ticket_category_id = settings.get("ticket_category_id", "") or ""
    ticket_banner_url = settings.get("ticket_banner_url", "") or ""
    transcript_status = settings.get("transcript_enabled", True)
    close_reason_status = settings.get("close_reason_enabled", True)

    banned_words_list = settings.get("banned_words", ["scam", "nitro-free"])
    banned_words_text = "\n".join(banned_words_list)

    ticket_sections = settings.get("ticket_sections", [
        {"emoji": "📌", "label": "General Support", "desc": "Standard general assistance query lines."}
    ])
    sections_text = "\n".join([f"{s['emoji']} | {s['label']} | {s['desc']}" for s in ticket_sections])

    return f"""
    <html>
        <head>
            <title>Managing {guild.name}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ {GLOBAL_BODY_STYLE} }}
                .card {{ background: #2c2f33; padding: 35px; max-width: 650px; margin: 0 auto; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.25); border: 1px solid #4f545c; }}
                .toggle-section {{ display: flex; justify-content: space-between; align-items: center; margin: 16px 0; padding: 14px 18px; background: #202225; border-radius: 8px; border: 1px solid #2f3136; }}
                .switch {{ position: relative; display: inline-block; width: 50px; height: 26px; }}
                .switch input {{ opacity: 0; width: 0; height: 0; }}
                .slider {{ position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #4f545c; transition: .3s; border-radius: 34px; }}
                .slider:before {{ position: absolute; content: ""; height: 18px; width: 18px; left: 4px; bottom: 4px; background-color: white; transition: .3s; border-radius: 50%; }}
                input:checked + .slider {{ background-color: #43b581; }}
                input:checked + .slider:before {{ transform: translateX(24px); }}
                .input-field {{ width: 100%; padding: 12px; background: #40444b; color: white; border: 1px solid #202225; border-radius: 6px; box-sizing: border-box; font-size: 14px; margin-top: 5px; transition: border 0.2s; }}
                .input-field:focus {{ border: 1px solid #7289da; outline: none; }}
                .input-group {{ margin: 22px 0; padding: 18px; background: #202225; border-radius: 8px; border: 1px solid #2f3136; }}
                label {{ display: block; font-weight: 600; font-size: 14px; color: #dcddde; }}
                .subtext {{ font-size: 12px; color: #72767d; margin-top: 6px; font-weight: normal; }}
                .back-btn {{ display: inline-block; color: #b9bbbe; text-decoration: none; font-size: 14px; margin-bottom: 20px; font-weight: 500; }}
                .back-btn:hover {{ color: #ffffff; }}
            </style>
        </head>
        <body>
            <div class="card">
                <a href="/dashboard" class="back-btn">⬅️ Back to Server Hub</a>
                <h1 style="margin: 0 0 8px 0; font-size: 24px; font-weight: bold;">⚙️ {guild.name}</h1>
                <p style="color:#b9bbbe; margin: 0 0 30px 0; font-size: 14px;">Running on Ender Bot v2.0 Platform Infrastructure</p>
                
                <form action="/manage/{guild_id}/update" method="POST">
                    
                    <div class="toggle-section">
                        <div><strong>🛡️ AutoMod Core Defenses</strong><div class="subtext">Blocks filtered textual phrases globally.</div></div>
                        <label class="switch"><input type="checkbox" name="automod" {"checked" if automod_status else ""}><span class="slider"></span></label>
                    </div>
                    <div class="toggle-section">
                        <div><strong>🔨 Administrative Commands</strong><div class="subtext">Allows execution of interaction tracking matrices.</div></div>
                        <label class="switch"><input type="checkbox" name="mod_cmds" {"checked" if mod_cmds_status else ""}><span class="slider"></span></label>
                    </div>
                    <div class="toggle-section">
                        <div><strong>📜 Dynamic Ticket Transcripts</strong><div class="subtext">Compiles channel records to .txt logs upon room teardown.</div></div>
                        <label class="switch"><input type="checkbox" name="transcript_enabled" {"checked" if transcript_status else ""}><span class="slider"></span></label>
                    </div>
                    <div class="toggle-section">
                        <div><strong>✍️ Force Reason Verification</strong><div class="subtext">Requires staff reasons before closing communication lines.</div></div>
                        <label class="switch"><input type="checkbox" name="close_reason_enabled" {"checked" if close_reason_status else ""}><span class="slider"></span></label>
                    </div>

                    <div class="input-group">
                        <label>📝 Auditing Logging Channel ID</label>
                        <input type="text" name="logging_channel" value="{logging_channel_id}" class="input-field" placeholder="e.g. 1503037186034110595">
                        <div class="subtext">Target data line where execution state actions log out.</div>
                    </div>
                    <div class="input-group">
                        <label>📂 Support Category Parent ID</label>
                        <input type="text" name="ticket_category" value="{ticket_category_id}" class="input-field" placeholder="e.g. 1503357008722530377">
                        <div class="subtext">The category wrapper layout where new private spaces spawn.</div>
                    </div>
                    <div class="input-group">
                        <label>🖼️ Ticket Main Header Embed Banner URL</label>
                        <input type="text" name="ticket_banner" value="{ticket_banner_url}" class="input-field" placeholder="https://domain.com/asset.png">
                        <div class="subtext">Visual image attached inside dashboard setup alerts.</div>
                    </div>
                    <div class="input-group">
                        <label>🚫 AutoMod Term Filter List (One string per line)</label>
                        <textarea name="banned_words_raw" rows="4" class="input-field" style="resize: vertical;" placeholder="scam&#10;exploit">{banned_words_text}</textarea>
                    </div>
                    <div class="input-group">
                        <label>🗂️ Ticket Structural Departments (Emoji | Heading Label | Description)</label>
                        <textarea name="ticket_sections_raw" rows="4" class="input-field" style="resize: vertical; font-family: monospace;" placeholder="📌 | Billing Support | Payment tasks processing.">{sections_text}</textarea>
                        <div class="subtext">Separate sections using the strict vertical pipelining string style.</div>
                    </div>

                    <button type="submit" style="background:#5865F2;color:white;border:none;padding:15px;font-weight:bold;border-radius:6px;cursor:pointer;width:100%;font-size:16px;box-shadow: 0 4px 12px rgba(88, 101, 242, 0.2); transition: background 0.2s;">Save Operational Configurations</button>
                </form>
            </div>
        </body>
    </html>
    """

@app.route("/manage/<int:guild_id>/update", methods=["POST"])
async def update_server_settings(guild_id):
    if not session.get("discord_token"): 
        return redirect(url_for("login"))
    form = await request.form
    
    automod_enabled = "automod" in form
    mod_cmds_enabled = "mod_cmds" in form
    transcript_enabled = "transcript_enabled" in form
    close_reason_enabled = "close_reason_enabled" in form
    
    log_ch = form.get("logging_channel", "").strip()
    logging_channel_id = int(log_ch) if log_ch.isdigit() else None

    tick_cat = form.get("ticket_category", "").strip()
    ticket_category_id = int(tick_cat) if tick_cat.isdigit() else None

    ticket_banner = form.get("ticket_banner", "").strip()

    raw_words = form.get("banned_words_raw", "").strip()
    parsed_words = [w.strip().lower() for w in raw_words.split("\n") if w.strip()]

    raw_sections = form.get("ticket_sections_raw", "").strip()
    parsed_sections = []
    if raw_sections:
        for line in raw_sections.split("\n"):
            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 3:
                    parsed_sections.append({"emoji": parts[0], "label": parts[1], "desc": parts[2]})

    config_collection = db_manager.get_collection("guild_settings")
    await config_collection.update_one(
        {"guild_id": guild_id},
        {"$set": {
            "automod_enabled": automod_enabled,
            "mod_cmds_enabled": mod_cmds_enabled,
            "transcript_enabled": transcript_enabled,
            "close_reason_enabled": close_reason_enabled,
            "logging_channel_id": logging_channel_id,
            "ticket_category_id": ticket_category_id,
            "ticket_banner_url": ticket_banner,
            "banned_words": parsed_words,
            "ticket_sections": parsed_sections
        }},
        upsert=True
    )
    return redirect(f"/manage/{guild_id}")

async def run_dashboard(bot, port: int):
    app.bot = bot
    from hypercorn.asyncio import serve
    from hypercorn.config import Config as HyperConfig
    hyper_config = HyperConfig()
    hyper_config.bind = [f"0.0.0.0:{port}"]
    await serve(app, hyper_config)
