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

# --- REUSABLE CYBER DESIGN BRANDING CONSTANTS ---
GLOBAL_BODY_STYLE = "font-family: 'Segoe UI', Inter, system-ui, sans-serif; background: #0f1115; color: #f2f3f5; padding: 40px; margin: 0; line-height: 1.5;"
NAV_BANNER_URL = "https://media.discordapp.net/attachments/1503357008722530377/1505483556959293628/11.png"

@app.route("/")
async def home():
    return f"""
    <html>
        <head>
            <title>Ender Bot Portal</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="{GLOBAL_BODY_STYLE} text-align: center; padding-top: 10vh; background: radial-gradient(circle at top, #1a1c24 0%, #0f1115 100%);">
            <div style="max-width: 480px; margin: 0 auto; background: #161920; padding: 45px; border-radius: 16px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.05);">
                <div style="overflow: hidden; border-radius: 10px; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.03);">
                    <img src="{NAV_BANNER_URL}" style="width: 100%; display: block; filter: brightness(0.95);">
                </div>
                <h1 style="margin-bottom: 15px; font-weight: 800; font-size: 26px; letter-spacing: 1px; color: #ffffff;">🤖 ENDER BOT PORTAL</h1>
                <p style="color: #9da2af; margin-bottom: 40px; font-size: 14px; font-weight: 400;">Manage automated queues, encrypted terminal logging maps, and multi-tier guild parameters seamlessly.</p>
                <a style="display: block; background: linear-gradient(135deg, #5865F2 0%, #4752C4 100%); color: #ffffff; padding: 16px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px; letter-spacing: 0.3px; box-shadow: 0 4px 15px rgba(88, 101, 242, 0.3); transition: all 0.2s ease;" href="/login">Connect Authorization Key</a>
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
            btn = f'<a href="/manage/{guild_id}" style="background: linear-gradient(135deg, #248046 0%, #1a6535 100%); color: white; padding: 10px 22px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 13px; box-shadow: 0 4px 12px rgba(36,128,70,0.25); border: 1px solid rgba(255,255,255,0.05);">Configure</a>'
        else:
            inv = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions=8&scope=bot%20applications.commands&guild_id={guild_id}&disable_guild_select=true"
            btn = f'<a href="{inv}" target="_blank" style="background: linear-gradient(135deg, #4f545c 0%, #3a3c40 100%); color: #dcddde; padding: 10px 22px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 13px; border: 1px solid rgba(255,255,255,0.03);">Deploy Bot</a>'
        
        guilds_html += f"""
        <div style="background: #161920; padding: 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.03); transition: transform 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
            <img src="{icon_url}" style="width: 48px; height: 48px; border-radius: 10px; margin-right: 20px; object-fit: cover; border: 1px solid rgba(255,255,255,0.05);">
            <div style="flex-grow: 1;">
                <span style="font-weight: 600; font-size: 16px; letter-spacing: 0.3px; color: #ffffff;">{guild_name}</span>
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
            <div style="max-width: 800px; margin: 0 auto;">
                <div style="flex; align-items: center; justify-content: space-between; margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 25px;">
                    <h2 style="margin: 0; font-weight: 700; font-size: 22px;">Welcome, {user_data.get("username", "Admin")} 👋</h2>
                    <span style="background: rgba(88, 101, 242, 0.15); color: #5865F2; border: 1px solid rgba(88, 101, 242, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 11px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">SYSTEM MAINBOARD</span>
                </div>
                <h3 style="color: #9da2af; margin-bottom: 20px; font-size: 12px; font-transform: uppercase; letter-spacing: 1.5px; font-weight: 700;">Operational Clusters Available</h3>
                {guilds_html if guilds_html else '<p style="color:#b9bbbe;">No servers located with valid administrative validation tokens.</p>'}
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

    current_autorole_id = str(settings.get("autorole_id", ""))

    banned_words_list = settings.get("banned_words", ["scam", "nitro-free"])
    banned_words_text = "\n".join(banned_words_list)

    sorted_roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)
    role_options_html = '<option value="">⚠️ Disabled / No Automation Profile Assigned</option>'
    
    for r in sorted_roles:
        if r.is_default(): 
            continue
        is_active = "selected" if str(r.id) == current_autorole_id else ""
        role_options_html += f'<option value="{r.id}" {is_active}>@{r.name}</option>'

    return f"""
    <html>
        <head>
            <title>Configuring {guild.name}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ {GLOBAL_BODY_STYLE} }}
                .card {{ background: #161920; padding: 40px; max-width: 720px; margin: 0 auto; border-radius: 16px; box-shadow: 0 25px 60px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.05); }}
                .grid-sections {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 25px 0; }}
                .toggle-section {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: #0f1115; border-radius: 10px; border: 1px solid rgba(255,255,255,0.03); }}
                .switch {{ position: relative; display: inline-block; width: 44px; height: 24px; min-width: 44px; }}
                .switch input {{ opacity: 0; width: 0; height: 0; }}
                .slider {{ position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #3f4248; transition: .25s ease; border-radius: 34px; }}
                .slider:before {{ position: absolute; content: ""; height: 16px; width: 16px; left: 4px; bottom: 4px; background-color: white; transition: .25s ease; border-radius: 50%; }}
                input:checked + .slider {{ background-color: #23a55a; }}
                input:checked + .slider:before {{ transform: translateX(20px); }}
                .input-field {{ width: 100%; padding: 14px; background: #0f1115; color: #f2f3f5; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; box-sizing: border-box; font-size: 14px; margin-top: 8px; transition: all 0.2s ease; }}
                .input-field:focus {{ border: 1px solid #5865F2; background: #13161c; outline: none; box-shadow: 0 0 0 3px rgba(88, 101, 242, 0.15); }}
                .input-group {{ margin-bottom: 20px; padding: 22px; background: #0f1115; border-radius: 10px; border: 1px solid rgba(255,255,255,0.03); }}
                label {{ display: block; font-weight: 600; font-size: 14px; color: #ffffff; letter-spacing: 0.3px; }}
                .subtext {{ font-size: 12px; color: #9da2af; margin-top: 6px; font-weight: 400; }}
                .back-btn {{ display: inline-flex; align-items: center; color: #9da2af; text-decoration: none; font-size: 14px; margin-bottom: 25px; font-weight: 600; transition: color 0.2s; }}
                .back-btn:hover {{ color: #ffffff; }}
                @media(max-width: 768px) {{ .grid-sections {{ grid-template-columns: 1fr; }} }}
            </style>
        </head>
        <body>
            <div class="card">
                <a href="/dashboard" class="back-btn">📋 Return to Cluster Hub</a>
                <h1 style="margin: 0 0 6px 0; font-size: 26px; font-weight: 800; color: #ffffff;">⚙️ {guild.name}</h1>
                <p style="color: #9da2af; margin: 0 0 30px 0; font-size: 14px;">Operational Matrix Array • Ender Control Subsystem</p>
                
                <form action="/manage/{guild_id}/update" method="POST">
                    
                    <label style="font-size: 12px; text-transform: uppercase; color: #5865F2; letter-spacing: 1px; font-weight: 700; margin-bottom: 10px;">Security Modules Execution Switches</label>
                    <div class="grid-sections">
                        <div class="toggle-section">
                            <div><strong style="font-size:14px;">🛡️ Core AutoMod</strong><div class="subtext">Blocks filter arrays globally.</div></div>
                            <label class="switch"><input type="checkbox" name="automod" {"checked" if automod_status else ""}><span class="slider"></span></label>
                        </div>
                        <div class="toggle-section">
                            <div><strong style="font-size:14px;">🔨 Staff Directives</strong><div class="subtext">Allows tracked moderation parameters.</div></div>
                            <label class="switch"><input type="checkbox" name="mod_cmds" {"checked" if mod_cmds_status else ""}><span class="slider"></span></label>
                        </div>
                        <div class="toggle-section">
                            <div><strong style="font-size:14px;">📜 Ticket Archiver</strong><div class="subtext">Compiles dynamic chat transcripts.</div></div>
                            <label class="switch"><input type="checkbox" name="transcript_enabled" {"checked" if transcript_status else ""}><span class="slider"></span></label>
                        </div>
                        <div class="toggle-section">
                            <div><strong style="font-size:14px;">✍️ Enforced Auditing</strong><div class="subtext">Forces explicit reasons on close.</div></div>
                            <label class="switch"><input type="checkbox" name="close_reason_enabled" {"checked" if close_reason_status else ""}><span class="slider"></span></label>
                        </div>
                    </div>

                    <label style="font-size: 12px; text-transform: uppercase; color: #5865F2; letter-spacing: 1px; font-weight: 700; margin: 30px 0 10px 0;">Cluster Map Assignments</label>
                    
                    <div class="input-group">
                        <label>👥 Automatic Welcome Join Role</label>
                        <select name="autorole_id" class="input-field" style="cursor: pointer;">
                            {role_options_html}
                        </select>
                        <div class="subtext">The unique structural security clearance role auto-assigned instantly to human entities landing inside the grid map channels.</div>
                    </div>

                    <div class="input-group">
                        <label>📝 Active Incident Audit Logging Channel ID</label>
                        <input type="text" name="logging_channel" value="{logging_channel_id}" class="input-field" placeholder="e.g. 1503037186034110595">
                        <div class="subtext">Target data stream pipeline path where execution state triggers output.</div>
                    </div>
                    <div class="input-group">
                        <label>📂 Terminal Category Allocation ID</label>
                        <input type="text" name="ticket_category" value="{ticket_category_id}" class="input-field" placeholder="e.g. 1503357008722530377">
                        <div class="subtext">The dedicated container wrapper segment where new private secure lines map down.</div>
                    </div>
                    <div class="input-group">
                        <label>🖼️ Dashboard Frame Header Embed Image Canvas URL</label>
                        <input type="text" name="ticket_banner" value="{ticket_banner_url}" class="input-field" placeholder="https://domain.com/graphics-asset.png">
                        <div class="subtext">Visual image attached inside dashboard setup layouts.</div>
                    </div>
                    <div class="input-group">
                        <label>🚫 Real-Time Lexicon Term Filter Array (One target pattern per row)</label>
                        <textarea name="banned_words_raw" rows="4" class="input-field" style="resize: vertical; font-family: monospace; padding: 14px;" placeholder="scam&#10;exploit-payload">{banned_words_text}</textarea>
                    </div>

                    <button type="submit" style="background: linear-gradient(135deg, #5865F2 0%, #4752C4 100%); color: white; border: none; padding: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%; font-size: 15px; letter-spacing: 0.3px; box-shadow: 0 6px 20px rgba(88, 101, 242, 0.25); border: 1px solid rgba(255,255,255,0.05); transition: background 0.2s;">Commit Changes To Mainframe</button>
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

    raw_autorole = form.get("autorole_id", "").strip()
    autorole_id = int(raw_autorole) if raw_autorole.isdigit() else None

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
            "autorole_id": autorole_id
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
    await serve(app, hyper_config)                <h1 style="margin-bottom: 15px; font-weight: 800; font-size: 26px; letter-spacing: 1px; color: #ffffff;">🤖 ENDER BOT PORTAL</h1>
                <p style="color: #9da2af; margin-bottom: 40px; font-size: 14px; font-weight: 400;">Manage automated queues, encrypted terminal logging maps, and multi-tier guild parameters seamlessly.</p>
                <a style="display: block; background: linear-gradient(135deg, #5865F2 0%, #4752C4 100%); color: #ffffff; padding: 16px 30px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px; letter-spacing: 0.3px; box-shadow: 0 4px 15px rgba(88, 101, 242, 0.3); transition: all 0.2s ease;" href="/login">Connect Authorization Key</a>
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
            btn = f'<a href="/manage/{guild_id}" style="background: linear-gradient(135deg, #248046 0%, #1a6535 100%); color: white; padding: 10px 22px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 13px; box-shadow: 0 4px 12px rgba(36,128,70,0.25); border: 1px solid rgba(255,255,255,0.05);">Configure</a>'
        else:
            inv = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions=8&scope=bot%20applications.commands&guild_id={guild_id}&disable_guild_select=true"
            btn = f'<a href="{inv}" target="_blank" style="background: linear-gradient(135deg, #4f545c 0%, #3a3c40 100%); color: #dcddde; padding: 10px 22px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 13px; border: 1px solid rgba(255,255,255,0.03);">Deploy Bot</a>'
        
        guilds_html += f"""
        <div style="background: #161920; padding: 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 14px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.03); transition: transform 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
            <img src="{icon_url}" style="width: 48px; height: 48px; border-radius: 10px; margin-right: 20px; object-fit: cover; border: 1px solid rgba(255,255,255,0.05);">
            <div style="flex-grow: 1;">
                <span style="font-weight: 600; font-size: 16px; letter-spacing: 0.3px; color: #ffffff;">{guild_name}</span>
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
            <div style="max-width: 800px; margin: 0 auto;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 25px;">
                    <h2 style="margin: 0; font-weight: 700; font-size: 22px;">Welcome, {user_data.get("username", "Admin")} 👋</h2>
                    <span style="background: rgba(88, 101, 242, 0.15); color: #5865F2; border: 1px solid rgba(88, 101, 242, 0.3); padding: 6px 14px; border-radius: 20px; font-size: 11px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">SYSTEM MAINBOARD</span>
                </div>
                <h3 style="color: #9da2af; margin-bottom: 20px; font-size: 12px; font-transform: uppercase; letter-spacing: 1.5px; font-weight: 700;">Operational Clusters Available</h3>
                {guilds_html if guilds_html else '<p style="color:#b9bbbe;">No servers located with valid administrative validation tokens.</p>'}
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

    # Fetch currently assigned autorole value from database configurations
    current_autorole_id = str(settings.get("autorole_id", ""))

    banned_words_list = settings.get("banned_words", ["scam", "nitro-free"])
    banned_words_text = "\n".join(banned_words_list)

    # 🔥 GENERATE HIGHLY FORMALIZED ROLES OPTION MATRIX FOR DROPDOWN
    sorted_roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)
    role_options_html = '<option value="">⚠️ Disabled / No Automation Profile Assigned</option>'
    
    for r in sorted_roles:
        if r.is_default(): 
            continue
        is_active = "selected" if str(r.id) == current_autorole_id else ""
        role_options_html += f'<option value="{r.id}" {is_active}>@{r.name}</option>'

    return f"""
    <html>
        <head>
            <title>Configuring {guild.name}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ {GLOBAL_BODY_STYLE} }}
                .card {{ background: #161920; padding: 40px; max-width: 720px; margin: 0 auto; border-radius: 16px; box-shadow: 0 25px 60px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.05); }}
                .grid-sections {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 25px 0; }}
                .toggle-section {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: #0f1115; border-radius: 10px; border: 1px solid rgba(255,255,255,0.03); }}
                .switch {{ position: relative; display: inline-block; width: 44px; height: 24px; min-width: 44px; }}
                .switch input {{ opacity: 0; width: 0; height: 0; }}
                .slider {{ position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #3f4248; transition: .25s ease; border-radius: 34px; }}
                .slider:before {{ position: absolute; content: ""; height: 16px; width: 16px; left: 4px; bottom: 4px; background-color: white; transition: .25s ease; border-radius: 50%; }}
                input:checked + .slider {{ background-color: #23a55a; }}
                input:checked + .slider:before {{ transform: translateX(20px); }}
                .input-field {{ width: 100%; padding: 14px; background: #0f1115; color: #f2f3f5; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; box-sizing: border-box; font-size: 14px; margin-top: 8px; transition: all 0.2s ease; }}
                .input-field:focus {{ border: 1px solid #5865F2; background: #13161c; outline: none; box-shadow: 0 0 0 3px rgba(88, 101, 242, 0.15); }}
                .input-group {{ margin-bottom: 20px; padding: 22px; background: #0f1115; border-radius: 10px; border: 1px solid rgba(255,255,255,0.03); }}
                label {{ display: block; font-weight: 600; font-size: 14px; color: #ffffff; letter-spacing: 0.3px; }}
                .subtext {{ font-size: 12px; color: #9da2af; margin-top: 6px; font-weight: 400; }}
                .back-btn {{ display: inline-flex; align-items: center; color: #9da2af; text-decoration: none; font-size: 14px; margin-bottom: 25px; font-weight: 600; transition: color 0.2s; }}
                .back-btn:hover {{ color: #ffffff; }}
                @media(max-width: 768px) {{ .grid-sections {{ grid-template-columns: 1fr; }} }}
            </style>
        </head>
        <body>
            <div class="card">
                <a href="/dashboard" class="back-btn">📋 Return to Cluster Hub</a>
                <h1 style="margin: 0 0 6px 0; font-size: 26px; font-weight: 800; color: #ffffff;">⚙️ {guild.name}</h1>
                <p style="color: #9da2af; margin: 0 0 30px 0; font-size: 14px;">Operational Matrix Array • Ender Control Subsystem</p>
                
                <form action="/manage/{guild_id}/update" method="POST">
                    
                    <label style="font-size: 12px; text-transform: uppercase; color: #5865F2; letter-spacing: 1px; font-weight: 700; margin-bottom: 10px;">Security Modules Execution Switches</label>
                    <div class="grid-sections">
                        <div class="toggle-section">
                            <div><strong style="font-size:14px;">🛡️ Core AutoMod</strong><div class="subtext">Blocks filter arrays globally.</div></div>
                            <label class="switch"><input type="checkbox" name="automod" {"checked" if automod_status else ""}><span class="slider"></span></label>
                        </div>
                        <div class="toggle-section">
                            <div><strong style="font-size:14px;">🔨 Staff Directives</strong><div class="subtext">Allows tracked moderation parameters.</div></div>
                            <label class="switch"><input type="checkbox" name="mod_cmds" {"checked" if mod_cmds_status else ""}><span class="slider"></span></label>
                        </div>
                        <div class="toggle-section">
                            <div><strong style="font-size:14px;">📜 Ticket Archiver</strong><div class="subtext">Compiles dynamic chat transcripts.</div></div>
                            <label class="switch"><input type="checkbox" name="transcript_enabled" {"checked" if transcript_status else ""}><span class="slider"></span></label>
                        </div>
                        <div class="toggle-section">
                            <div><strong style="font-size:14px;">✍️ Enforced Auditing</strong><div class="subtext">Forces explicit reasons on close.</div></div>
                            <label class="switch"><input type="checkbox" name="close_reason_enabled" {"checked" if close_reason_status else ""}><span class="slider"></span></label>
                        </div>
                    </div>

                    <label style="font-size: 12px; text-transform: uppercase; color: #5865F2; letter-spacing: 1px; font-weight: 700; margin: 30px 0 10px 0;">Cluster Map Assignments</label>
                    
                    <div class="input-group">
                        <label>👥 Automatic Welcome Join Role</label>
                        <select name="autorole_id" class="input-field" style="cursor: pointer;">
                            {role_options_html}
                        </select>
                        <div class="subtext">The unique structural security clearance role auto-assigned instantly to human entities landing inside the grid map channels.</div>
                    </div>

                    <div class="input-group">
                        <label>📝 Active Incident Audit Logging Channel ID</label>
                        <input type="text" name="logging_channel" value="{logging_channel_id}" class="input-field" placeholder="e.g. 1503037186034110595">
                        <div class="subtext">Target data stream pipeline path where execution state triggers output.</div>
                    </div>
                    <div class="input-group">
                        <label>📂 Terminal Category Allocation ID</label>
                        <input type="text" name="ticket_category" value="{ticket_category_id}" class="input-field" placeholder="e.g. 1503357008722530377">
                        <div class="subtext">The dedicated container wrapper segment where new private secure lines map down.</div>
                    </div>
                    <div class="input-group">
                        <label>🖼️ Dashboard Frame Header Embed Image Canvas URL</label>
                        <input type="text" name="ticket_banner" value="{ticket_banner_url}" class="input-field" placeholder="https://domain.com/graphics-asset.png">
                        <div class="subtext">Visual image attached inside dashboard setup layouts.</div>
                    </div>
                    <div class="input-group">
                        <label>🚫 Real-Time Lexicon Term Filter Array (One target pattern per row)</label>
                        <textarea name="banned_words_raw" rows="4" class="input-field" style="resize: vertical; font-family: monospace; padding: 14px;" placeholder="scam&#10;exploit-payload">{banned_words_text}</textarea>
                    </div>

                    <button type="submit" style="background: linear-gradient(135deg, #5865F2 0%, #4752C4 100%); color: white; border: none; padding: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%; font-size: 15px; letter-spacing: 0.3px; box-shadow: 0 6px 20px rgba(88, 101, 242, 0.25); border: 1px solid rgba(255,255,255,0.05); transition: background 0.2s;">Commit Changes To Mainframe</button>
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

    # Parse and extract incoming automated authorization identity field string to safe int configuration
    raw_autorole = form.get("autorole_id", "").strip()
    autorole_id = int(raw_autorole) if raw_autorole.isdigit() else None

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
            "autorole_id": autorole_id
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
    await serve(app, hyper_config)                <a style="display: block; background: #5865F2; color: #ffffff; padding: 16px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; transition: background 0.2s;" href="/login">Log In With Discord</a>
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
            "banned_words": parsed_words
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
