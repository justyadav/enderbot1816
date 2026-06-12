import os
import logging
import aiohttp
from quart import Quart, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv

# Initialize configurations
load_dotenv()
logger = logging.getLogger("Bot.Dashboard")

app = Quart(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

app.bot = None 

@app.before_serving
async def init_dashboard():
    logger.info("Starting Web Dashboard engine...")

@app.route("/")
async def home():
    return """
    <html>
        <head>
            <title>Ender Bot Portal</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; background: #23272a; color: white; text-align: center; padding-top: 100px; }
                .btn { background: #5865F2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px; display: inline-block; margin-top: 20px; transition: 0.2s; }
                .btn:hover { background: #4752C4; }
                h1 { color: #7289da; }
            </style>
        </head>
        <body>
            <h1>🤖 ENDER BOT 2.O Portal</h1>
            <p>Manage your servers, track automod operations, and configure settings live.</p>
            <a class="btn" href="/login">Log In With Discord</a>
        </body>
    </html>
    """

@app.route("/login")
async def login():
    # Crucial: The scope must explicitly contain both 'identify' and 'guilds'
    oauth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&response_type=code&scope=identify%20guilds"
    )
    return redirect(oauth_url)

@app.route("/callback")
async def callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    async with aiohttp.ClientSession() as session_client:
        async with session_client.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers) as resp:
            token_json = await resp.json()
            if resp.status != 200:
                return jsonify({"error": "Failed to exchange OAuth token", "details": token_json}), 400
            
            session["discord_token"] = token_json.get("access_token")
            return redirect(url_for("user_dashboard"))

@app.route("/dashboard")
async def user_dashboard():
    token = session.get("discord_token")
    if not token:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session_client:
        # 1. Fetch User Data
        async with session_client.get("https://discord.com/api/v10/users/@me", headers=headers) as user_resp:
            if user_resp.status != 200:
                session.clear()
                return redirect(url_for("login"))
            user_data = await user_resp.json()

        # 2. Fetch User's Guilds (Servers)
        async with session_client.get("https://discord.com/api/v10/users/@me/guilds", headers=headers) as guilds_resp:
            if guilds_resp.status != 200:
                return "Failed to fetch your servers from Discord.", 500
            all_guilds = await guilds_resp.json()

    # Get a list of guild IDs that the bot is already in
    bot_guild_ids = [guild.id for guild in app.bot.guilds] if app.bot else []

    # Generate the HTML list elements for the servers
    guilds_html = ""
    for g in all_guilds:
        # Check permissions using the bitwise ADMINISTRATOR flag (0x8)
        permissions = int(g.get("permissions", 0))
        is_admin = (permissions & 0x8) == 0x8

        # Only display servers where the user has Admin rights
        if not is_admin:
            continue

        guild_id = int(g["id"])
        guild_name = g["name"]
        icon_hash = g.get("icon")
        
        # Build server icon URL or use fallback initials icon
        if icon_hash:
            icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{icon_hash}.png"
        else:
            icon_url = "https://cdn.discordapp.com/embed/avatars/0.png"

        # Determine if bot is in server or needs to be invited
        if guild_id in bot_guild_ids:
            action_button = f'<a href="/manage/{guild_id}" class="btn btn-manage">Manage</a>'
        else:
            # Dynamically attach permissions=8 (Admin) and the target guild_id to the invite URL
            invite_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&permissions=8&scope=bot%20applications.commands&guild_id={guild_id}&disable_guild_select=true"
            action_button = f'<a href="{invite_url}" target="_blank" class="btn btn-invite">Invite Bot</a>'

        guilds_html += f"""
        <div class="server-card">
            <img src="{icon_url}" alt="{guild_name} Icon">
            <div class="server-info">
                <span class="server-name">{guild_name}</span>
            </div>
            {action_button}
        </div>
        """

    # User avatar processing fallback layout
    avatar_hash = user_data.get('avatar')
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{avatar_hash}.png" if avatar_hash else "https://cdn.discordapp.com/embed/avatars/0.png"

    return f"""
    <html>
        <head>
            <title>Ender Bot Control Panel</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #23272a; color: white; margin: 0; padding: 20px; }}
                .container {{ max-width: 900px; margin: 0 auto; }}
                .header {{ background: #2c2f33; padding: 20px; border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; border: 1px solid #7289da; }}
                .header img {{ border-radius: 50%; border: 2px solid #7289da; margin-right: 20px; }}
                .header h2 {{ margin: 0; color: #7289da; }}
                .servers-list {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
                @media(max-width: 768px) {{ .servers-list {{ grid-template-columns: 1fr; }} }}
                .server-card {{ background: #2c2f33; padding: 15px; border-radius: 8px; display: flex; align-items: center; border: 1px solid #23272a; transition: 0.2s; }}
                .server-card:hover {{ border-color: #7289da; }}
                .server-card img {{ width: 50px; height: 50px; border-radius: 50%; margin-right: 15px; }}
                .server-info {{ flex-grow: 1; }}
                .server-name {{ font-weight: bold; font-size: 16px; display: block; }}
                .btn {{ text-decoration: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; font-size: 14px; text-align: center; transition: 0.2s; }}
                .btn-manage {{ background: #43b581; color: white; }}
                .btn-manage:hover {{ background: #3ca374; }}
                .btn-invite {{ background: #5865F2; color: white; }}
                .btn-invite:hover {{ background: #4752C4; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="{avatar_url}" width="60" height="60"/>
                    <div>
                        <h2>Hello, {user_data.get('global_name', user_data['username'])}</h2>
                        <p style="margin: 5px 0 0 0; color: #b9bbbe;">Select an accessible server to configure Ender Bot settings.</p>
                    </div>
                </div>
                <h3>Your Servers</h3>
                <div class="servers-list">
                    {guilds_html if guilds_html else '<p style="color: #b9bbbe;">No servers found where you have Administrative privileges.</p>'}
                </div>
            </div>
        </body>
    </html>
    """

@app.route("/manage/<int:guild_id>")
async def manage_server(guild_id):
    token = session.get("discord_token")
    if not token:
        return redirect(url_for("login"))

    if not app.bot:
        return "Bot application is currently initializing.", 503

    guild = app.bot.get_guild(guild_id)
    if not guild:
        return "Bot is not in this server or cache is unsynced.", 404

    # This acts as an administration interface page stub for your selected server
    return f"""
    <html>
        <head>
            <title>Managing {guild.name}</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: #23272a; color: white; padding: 50px; text-align: center; }}
                .card {{ background: #2c2f33; padding: 30px; display: inline-block; border-radius: 12px; border: 1px solid #43b581; }}
                .btn-back {{ display: inline-block; margin-top: 20px; color: #7289da; text-decoration: none; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>⚙️ {guild.name} Configuration</h1>
                <p>Server ID: <code>{guild.id}</code></p>
                <p>Total Members: <strong>{guild.member_count}</strong></p>
                <hr style="border-color: #23272a; margin: 20px 0;">
                <p style="color: #b9bbbe;">Database connections are ready. Admin features for Automod and Logs are live.</p>
                <a href="/dashboard" class="btn-back">← Back to Server Selection</a>
            </div>
        </body>
    </html>
    """

async def run_dashboard(bot, port: int):
    app.bot = bot
    
    from hypercorn.asyncio import serve
    from hypercorn.config import Config as HyperConfig
    
    hyper_config = HyperConfig()
    hyper_config.bind = [f"0.0.0.0:{port}"]
    
    logger.info(f"Dashboard routing active on port {port}")
    await serve(app, hyper_config)
