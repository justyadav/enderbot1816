from database import db_manager

@app.route("/manage/<int:guild_id>", methods=["GET"])
async def manage_server(guild_id):
    token = session.get("discord_token")
    if not token:
        return redirect(url_for("login"))

    if not app.bot:
        return "Bot application is currently initializing.", 503

    guild = app.bot.get_guild(guild_id)
    if not guild:
        return "Bot is not in this server or cache is unsynced.", 404

    # Fetch existing server configurations from MongoDB
    config_collection = db_manager.get_collection("guild_settings")
    settings = await config_collection.find_one({"guild_id": guild_id}) or {}
    
    # Default features to True (On) if they don't exist in the database yet
    automod_status = settings.get("automod_enabled", True)
    mod_cmds_status = settings.get("mod_cmds_enabled", True)

    return f"""
    <html>
        <head>
            <title>Managing {guild.name}</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: #23272a; color: white; padding: 40px; }}
                .card {{ background: #2c2f33; padding: 30px; max-width: 500px; margin: 0 auto; border-radius: 12px; border: 1px solid #7289da; }}
                h1 {{ color: #7289da; margin-top: 0; }}
                .toggle-section {{ display: flex; justify-content: space-between; align-items: center; margin: 20px 0; padding: 10px; background: #23272a; border-radius: 6px; }}
                .switch {{ position: relative; display: inline-block; width: 60px; height: 34px; }}
                .switch input {{ opacity: 0; width: 0; height: 0; }}
                .slider {{ position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }}
                .slider:before {{ position: absolute; content: ""; height: 26px; width: 26px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }}
                input:checked + .slider {{ background-color: #43b581; }}
                input:checked + .slider:before {{ transform: translateX(26px); }}
                .btn-save {{ background: #5865F2; color: white; border: none; padding: 10px 20px; font-weight: bold; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 10px; }}
                .btn-save:hover {{ background: #4752C4; }}
                .btn-back {{ display: block; text-align: center; margin-top: 20px; color: #b9bbbe; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>⚙️ {guild.name} Modules</h1>
                <p>Toggle features on or off instantly.</p>
                <form action="/manage/{guild_id}/update" method="POST">
                    
                    <div class="toggle-section">
                        <div>
                            <strong>🛡️ AutoMod System</strong>
                            <div style="font-size: 12px; color: #b9bbbe;">Filters bad words & links</div>
                        </div>
                        <label class="switch">
                            <input type="checkbox" name="automod" {"checked" if automod_status else ""}>
                            <span class="slider"></span>
                        </label>
                    </div>

                    <div class="toggle-section">
                        <div>
                            <strong>🔨 Moderation Commands</strong>
                            <div style="font-size: 12px; color: #b9bbbe;">Enables /kick, /ban, /mute</div>
                        </div>
                        <label class="switch">
                            <input type="checkbox" name="mod_cmds" {"checked" if mod_cmds_status else ""}>
                            <span class="slider"></span>
                        </label>
                    </div>

                    <button type="submit" class="btn-save">Save Configurations</button>
                </form>
                <a href="/dashboard" class="btn-back">← Back to Server Selection</a>
            </div>
        </body>
    </html>
    """

@app.route("/manage/<int:guild_id>/update", methods=["POST"])
async def update_server_settings(guild_id):
    token = session.get("discord_token")
    if not token:
        return redirect(url_for("login"))

    form = await request.form
    # If the checkbox is checked, its value is in the form data. If unchecked, it's completely missing.
    automod_enabled = "automod" in form
    mod_cmds_enabled = "mod_cmds" in form

    config_collection = db_manager.get_collection("guild_settings")
    
    # Save options to MongoDB
    await config_collection.update_one(
        {"guild_id": guild_id},
        {"$set": {
            "automod_enabled": automod_enabled,
            "mod_cmds_enabled": mod_cmds_enabled
        }},
        upsert=True
    )

    # Redirect back to the management page with updated switches
    return redirect(f"/manage/{guild_id}")
