import os
import logging
import aiohttp
from quart import Quart, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv

# Initialize environment variables and logging
load_dotenv()
logger = logging.getLogger("Bot.Dashboard")

app = Quart(__name__)
# Set a fallback secret key if one isn't provided in the .env file
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

# Configuration variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Bot instance dependency injection placeholder
app.bot = None 

@app.before_serving
async def init_dashboard():
    logger.info("Starting Web Dashboard engine...")

@app.route("/")
async def home():
    if app.bot:
        return jsonify({
            "status": "online",
            "bot_name": str(app.bot.user),
            "guilds_count": len(app.bot.guilds),
            "cached_users": len(app.bot.users)
        })
    return jsonify({"status": "starting_up"}), 503

@app.route("/login")
async def login():
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
            
            # Securely store the token in the encrypted cookie session
            session["discord_token"] = token_json.get("access_token")
            return redirect(url_for("user_dashboard"))

@app.route("/dashboard")
async def user_dashboard():
    token = session.get("discord_token")
    if not token:
        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session_client:
        async with session_client.get("https://discord.com/api/v10/users/@me", headers=headers) as user_resp:
            if user_resp.status != 200:
                session.clear()
                return redirect(url_for("login"))
                
            user_data = await user_resp.json()
            
            # Formulate the avatar URL (handle default avatars if the user doesn't have a custom one)
            avatar_hash = user_data.get('avatar')
            if avatar_hash:
                avatar_url = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{avatar_hash}.png"
            else:
                # Default fallback avatar calculation
                default_avatar = int(user_data.get('discriminator', 0)) % 5 if user_data.get('discriminator') != '0' else (int(user_data['id']) >> 22) % 6
                avatar_url = f"https://cdn.discordapp.com/embed/avatars/{default_avatar}.png"

            return f"""
            <html>
                <head>
                    <title>Ender Bot Control Panel</title>
                    <style>
                        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #23272a; color: white; text-align: center; padding-top: 50px; }}
                        .card {{ background: #2c2f33; padding: 30px; display: inline-block; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 1px solid #7289da; }}
                        img {{ border-radius: 50%; border: 3px solid #7289da; margin-bottom: 15px; }}
                        h2 {{ margin: 10px 0; color: #7289da; }}
                        p {{ margin: 8px 0; color: #b9bbbe; }}
                        .status {{ color: #43b581; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <div class="card">
                        <img src="{avatar_url}" width="100" alt="Avatar"/>
                        <h2>Welcome, {user_data.get('global_name', user_data['username'])}!</h2>
                        <p>Username: @{user_data['username']}</p>
                        <p>Bot Status: <span class="status">Online</span></p>
                        <p>Connected Servers: {len(app.bot.guilds) if app.bot else 0}</p>
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