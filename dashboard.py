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

@app.route("/")
async def home():
    return """
    <html>
        <head><title>Ender Bot Portal</title></head>
        <body style="font-family: sans-serif; background: #23272a; color: white; text-align: center; padding-top: 100px;">
            <h1>🤖 ENDER BOT 2.O Portal</h1>
            <a style="background: #5865F2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;" href="/login">Log In With Discord</a>
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
    if not code: return "Missing authorized callback identity token context", 400
    data = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'authorization_code', 'code': code, 'redirect_uri': REDIRECT_URI}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    async with aiohttp.ClientSession() as session_client:
        async with session_client.post("https://discord.com/api/oauth2/token", data=data, headers=headers) as resp:
            token_json = await resp.json()
            if resp.status != 200: return "OAuth execution token exchange sequence error.", 400
            session["discord_token"] = token_json.get("access_token")
            return redirect(url_for("user_dashboard"))

@app.route("/dashboard")
async def user_dashboard():
    token = session.get("discord_token")
    if not token: return redirect(url_for("login"))
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session_client:
        async with session_client.get("https://discord.com/api/v10/users/@me", headers=headers) as u_resp:
            user_data = await u_resp.json()
        async with session_client.get("https://discord.com/api/v10/users/@me/guilds", headers=headers) as g_resp:
            all_guilds = await g_resp.json()

    bot_guild_ids = [guild.id for guild in app.bot.guilds] if (app.bot and app.bot.is_ready()) else []
    guilds_html = ""
    for g in all_guilds:
        if not (int(g.get("permissions", 0)) & 0x8 == 0x8): continue
        guild_id, guild_name = int(g["id"]), g["name"]
        icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{g.get('icon')}.png" if g.get('icon') else "https://cdn.discordapp.com/embed/avatars/0.png"
        
        if guild_id in bot_guild_ids:
            btn = f'<a href="/manage/{guild_id}" style="background:#43b581;color:white;padding:8px 16px;text-decoration:none;border-radius:4px;font-weight:bold;">Manage</a>'
        else:
            inv = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions=8&scope=bot%20applications.commands&guild_id={guild_id}&disable_guild_select=true"
            btn = f'<a href="{inv}" target="_blank" style="background:#5865F2;color:white;padding:8px 16px;text-decoration:none;border-radius:4px;font-weight:bold;">Invite</a>'
        
        guilds_html += f'<div style="background:#2c2f33;padding:15px;border-radius:8px;display:flex;align-items:center;margin-bottom:10px;"><img src="{icon_url}" style="width:50px;height:50px;border-radius:50%;margin-right:15px;"><div style="flex-grow:1;"><span style="font-weight:bold;">{guild_name}</span></div>{btn}</div>'

    return f'<html><body style="font-family:sans-serif;background:#23272a;color:white;padding:20px;"><div style="max-width:800px;margin:0 auto;"><h2>Hello, {user_data.get("username")}</h2><h3>Your Admin Servers</h3>{guilds_html}</div></body></html>'

@app.route("/manage/<int:guild_id>", methods=["GET"])
async def manage_server(guild_id):
    if not session.get("discord_token"): return redirect(url_for("login"))
    if not app.bot: return "Initializing...", 503
    guild = app.bot.get_guild(guild_id)
    if not guild: return "Bot cache misaligned.", 404

    config_collection = db_manager.get_collection("guild_settings")
    settings = await config_collection.find_one({"guild_id": guild_id}) or {}
    
    automod_status = settings.get("automod_enabled", True)
    mod_cmds_status = settings.get("mod_cmds_enabled", True)
    logging_channel_id = settings.get("logging_channel_id", "")
    ticket_category_id = settings.get("ticket_category_id", "")
    ticket_banner_url = settings.get("ticket_banner_url", "")
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
            <style>
                body {{ font-family: sans-serif; background: #23272a; color: white; padding: 40px; }}
                .card {{ background: #2c2f33; padding: 30px; max-width: 600px; margin: 0 auto; border-radius: 12px; border: 1px solid #7289da; }}
                .toggle-section {{ display: flex; justify-content: space-between; align-items: center; margin: 20px 0; padding: 10px; background: #23272a; border-radius: 6px; }}
                .switch {{ position: relative; display: inline-block; width: 60px; height: 34px; }}
                .switch input {{ opacity: 0; width: 0; height: 0; }}
                .slider {{ position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }}
                .slider:before {{ position: absolute; content: ""; height: 26px; width: 26px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }}
                input:checked + .slider {{ background-color: #43b581; }}
                input:checked + .slider:before {{ transform: translateX(26px); }}
                .input-field {{ width: 100%; padding: 10px; background: #40444b; color: white; border: 1px solid #7289da; border-radius: 4px; box-sizing: border-box; }}
                .input-group {{ margin: 20px 0; padding: 15px; background: #23272a; border-radius: 6px; }}
                label {{ display: block; font-weight: bold; margin-bottom: 8px; }}
                .subtext {{ font-size: 12px; color: #b9bbbe; margin-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>⚙️ {guild.name} Control Panel</h1>
                <form action="/manage/{guild_id}/update" method="POST">
                    
                    <div class="toggle-section">
                        <div><strong>🛡️ AutoMod System</strong></div>
                        <label class="switch"><input type="checkbox" name="automod" {"checked" if automod_status else ""}><span class="slider"></span></label>
                    </div>
                    <div class="toggle-section">
                        <div><strong>🔨 Moderation Commands</strong></div>
                        <label class="switch"><input type="checkbox" name="mod_cmds" {"checked" if mod_cmds_status else ""}><span class="slider"></span></label>
                    </div>
                    <div class="toggle-section">
                        <div><strong>📜 Ticket Transcripts</strong></div>
                        <label class="switch"><input type="checkbox" name="transcript_enabled" {"checked" if transcript_status else ""}><span class="slider"></span></label>
                    </div>
                    <div class="toggle-section">
                        <div><strong>✍️ Close with Reason</strong></div>
                        <label class="switch"><input type="checkbox" name="close_reason_enabled" {"checked" if close_reason_status else ""}><span class="slider"></span></label>
                    </div>

                    <div class="input-group">
                        <label>📝 Logging Channel ID</label>
                        <input type="text" name="logging_channel" value="{logging_channel_id}" class="input-field">
                    </div>
                    <div class="input-group">
                        <label>📂 Ticket Parent Category ID</label>
                        <input type="text" name="ticket_category" value="{ticket_category_id}" class="input-field">
                    </div>
                    <div class="input-group">
                        <label>🖼️ Ticket Embed Banner URL</label>
                        <input type="text" name="ticket_banner" value="{ticket_banner_url}" class="input-field">
                    </div>
                    <div class="input-group">
                        <label>🚫 AutoMod Banned Words (One per line)</label>
                        <textarea name="banned_words_raw" rows="4" class="input-field">{banned_words_text}</textarea>
                    </div>
                    <div class="input-group">
                        <label>🗂️ Ticket Departments (Emoji | Label | Description)</label>
                        <textarea name="ticket_sections_raw" rows="5" class="input-field">{sections_text}</textarea>
                    </div>

                    <button type="submit" style="background:#5865F2;color:white;border:none;padding:14px;font-weight:bold;border-radius:4px;cursor:pointer;width:100%;font-size:16px;">Save Server Settings</button>
                </form>
            </div>
        </body>
    </html>
    """

@app.route("/manage/<int:guild_id>/update", methods=["POST"])
async def update_server_settings(guild_id):
    if not session.get("discord_token"): return redirect(url_for("login"))
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
