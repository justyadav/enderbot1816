import discord
from discord import app_commands
from discord.ext import commands
import io
import datetime
import asyncio

# --- SYSTEM BRANDING CONSTANTS ---
BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"

# --- REUSABLE HIGH-CONTRAST PALETTE ---
COLOR_MAIN_PANEL = discord.Color.from_rgb(47, 49, 54)     # Sleek Obsidian Grey
COLOR_ACTIVE_BLUE = discord.Color.from_rgb(114, 137, 218) # Discord Blurple Accent
COLOR_CONFIRM_GREEN = discord.Color.from_rgb(67, 181, 129) # Safe Mint Emerald
COLOR_ALERT_AMBER = discord.Color.from_rgb(250, 166, 26)   # Safety Warning Gold
COLOR_DANGER_RED = discord.Color.from_rgb(240, 71, 71)      # System Termination Crimson


# --- TICKET CONTROLS PANEL (Inside Active Tickets) ---
class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.success, custom_id="kite_pub_claim_btn", emoji="🤝", row=0)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Operational error: You lack `Manage Channels` clearance attributes.", ephemeral=True)
        
        button.disabled = True
        button.label = "Assigned to Staff"
        button.style = discord.ButtonStyle.secondary
        
        for item in self.children:
            if item.custom_id == "kite_pub_unclaim_btn":
                item.disabled = False

        await interaction.message.edit(view=self)

        embed = discord.Embed(
            title="⚡ Operational Assignment Locked",
            description=f"Support representative {interaction.user.mention} has taken formal ownership of this terminal thread.",
            color=COLOR_CONFIRM_GREEN
        )
        embed.set_footer(text=f"UID: {interaction.user.id} | {BRANDED_FOOTER}")
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Release", style=discord.ButtonStyle.danger, custom_id="kite_pub_unclaim_btn", emoji="🔄", disabled=True, row=0)
    async def unclaim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Operational error: Security token mismatch during update.", ephemeral=True)

        button.disabled = True
        
        for item in self.children:
            if item.custom_id == "kite_pub_claim_btn":
                item.disabled = False
                item.label = "Claim Ticket"
                item.style = discord.ButtonStyle.success

        await interaction.message.edit(view=self)

        embed = discord.Embed(
            description="⚠️ **Thread Disconnected:** The active owner has unassigned themselves. This incident track is open to other representatives.",
            color=COLOR_ALERT_AMBER
        )
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Transcript", style=discord.ButtonStyle.secondary, custom_id="kite_pub_transcript_btn", emoji="💾", row=1)
    async def transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        history_log = (
            f"✦ ━━━━━━━ Ender Bot Mainframe Transcript ━━━━━━━ ✦\n"
            f"Guild: {interaction.guild.name} ({interaction.guild.id})\n"
            f"Channel: #{interaction.channel.name} ({interaction.channel.id})\n"
            f"Compiled At: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"Export Key: {interaction.user.id}\n"
            f"━━━━━━━ • ━━━━━━━ • ━━━━━━━ • ━━━━━━━ • ━━━━━━━\n\n"
        )
        
        async for msg in interaction.channel.history(limit=None, oldest_first=True):
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            text = msg.content if msg.content else "[Data Object Array Content]"
            history_log += f"[{timestamp}] {msg.author.name}: {text}\n"
        
        file_bytes = io.BytesIO(history_log.encode('utf-8'))
        file = discord.File(file_bytes, filename=f"transcript-{interaction.channel.name}.txt")
        
        embed = discord.Embed(
            description="💾 **System Logs Compiled:** Active message history arrays have been securely zipped and exported.",
            color=COLOR_ACTIVE_BLUE
        )
        await interaction.followup.send(embed=embed, file=file, ephemeral=True)

    @discord.ui.button(label="Lock State", style=discord.ButtonStyle.secondary, custom_id="kite_pub_lock_btn", emoji="🔒", row=1)
    async def lock_room(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
            
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        for member in interaction.channel.overwrites:
            if isinstance(member, discord.Member) and not member.guild_permissions.manage_channels:
                await interaction.channel.set_permissions(member, send_messages=False, read_messages=True)

        embed = discord.Embed(
            title="🔒 Channel Input Frozen",
            description="This support instance is now placed under a hard lockdown state. Client communication lines are temporarily frozen.",
            color=COLOR_DANGER_RED
        )
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Terminate", style=discord.ButtonStyle.danger, custom_id="kite_pub_close_btn", emoji="🛑", row=1)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)

        embed = discord.Embed(
            title="⚠️ Terminating Ticket Instance",
            description="Deconstructing structural layout parameters.\nAll remaining cache logs are clearing permanently.\n\n`Deconstruction sequence: 5s`",
            color=COLOR_DANGER_RED
        )
        await interaction.response.send_message(embed=embed)
        
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason=f"Ticket terminated by {interaction.user}")
        except discord.NotFound:
            pass


# --- DROPDOWN WITH COMPONENT LIFECYCLE MEMORY ---
class TicketDropdown(discord.ui.Select):
    def __init__(self, category_id: int = None):
        self.category_id = category_id
        options = [
            discord.SelectOption(label="General Assistance", description="General queries, account roles, and help desk services.", emoji="⚙️", value="general"),
            discord.SelectOption(label="Billing & Operations", description="Inquiries matching shop packages, checkouts, and premium lines.", emoji="💳", value="billing"),
            discord.SelectOption(label="Core Security & Bugs", description="Report software errors, system faults, or user violations.", emoji="🛡️", value="report")
        ]
        super().__init__(
            placeholder="⚙️ Initialize a secure assistance pipeline...", 
            min_values=1, 
            max_values=1, 
            custom_id="kite_pub_persistent_select_menu", 
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        # Fallback tracking logic if global persistent view lost track of original category parameter
        category = guild.get_channel(self.category_id) if self.category_id else interaction.channel.category
        if not category:
            if hasattr(interaction.channel, "parent") and interaction.channel.parent:
                category = interaction.channel.parent
            else:
                return await interaction.followup.send("❌ Setup error: Missing target category structures.", ephemeral=True)

        prefix_map = {"general": "ticket-", "billing": "billing-", "report": "bug-"}
        prefix = prefix_map.get(self.values[0], "ticket-")
        
        clean_user_name = interaction.user.name.lower().replace(" ", "-")
        ticket_name = f"{prefix}{clean_user_name}"
        existing_channel = discord.utils.get(guild.channels, name=ticket_name)
        
        if existing_channel:
            error_embed = discord.Embed(
                description=f"❌ **Action Aborted:** You already have an active track in {existing_channel.mention}.",
                color=COLOR_DANGER_RED
            )
            return await interaction.followup.send(embed=error_embed, ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, read_message_history=True, embed_links=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True, manage_permissions=True)
        }

        for role in guild.roles:
            if role.permissions.manage_channels or role.permissions.administrator or role.permissions.manage_messages:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, read_message_history=True, embed_links=True)

        channel = await guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites=overwrites,
            topic=f"Active Support Ticket for {interaction.user.display_name} | Platform: {BOT_VERSION}"
        )

        success_creation_embed = discord.Embed(
            description=f"🚀 **Track Established Successfully!**\nYour direct terminal is waiting here: {channel.mention}",
            color=COLOR_CONFIRM_GREEN
        )
        await interaction.followup.send(embed=success_creation_embed, ephemeral=True)
        
        welcome_embed = discord.Embed(
            title=f"📥 Ticket Opened • Category: {self.values[0].capitalize()}",
            description=(
                f"Greetings {interaction.user.mention},\n\n"
                f"Welcome to your private help desk. A support agent will look over your details shortly.\n"
                f"To expedite this query, please explicitly state your issues in a brief, descriptive statement below."
            ),
            color=COLOR_ACTIVE_BLUE,
            timestamp=discord.utils.utcnow()
        )
        welcome_embed.add_field(
            name="✦ Guidelines & Policies", 
            value="```\n• Avoid unnecessary staff pings.\n• Provide clear, readable screenshot attachments.\n• Keep logs concise and direct.```", 
            inline=False
        )
        welcome_embed.set_footer(text=BRANDED_FOOTER)
        
        if guild.icon:
            welcome_embed.set_thumbnail(url=guild.icon.url)
            
        await channel.send(content=f"{interaction.user.mention} | Mainframe Notification", embed=welcome_embed, view=TicketControls())


# --- TICKET LAUNCH HUB PANEL ---
class TicketLauncher(discord.ui.View):
    def __init__(self, category_id: int = None):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown(category_id=category_id))


# =========================================================
# GLOBAL PUBLIC TICKETS COG
# =========================================================
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket_setup", description="Deploys the highly aesthetic ticket launcher dropdown configuration")
    @app_commands.describe(channel="Where the dashboard is deployed", category="Where active tickets live")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_cmd(self, interaction: discord.Interaction, channel: discord.TextChannel, category: discord.CategoryChannel):
        setup_embed = discord.Embed(
            title="✦ ━━━━━━━ Support Center Mainscreen ━━━━━━━ ✦",
            description=(
                f"Welcome to the **{interaction.guild.name}** Helpdesk.\n"
                f"If you require technical assistance, billing services, or account modifications, use the drop-down menu matrix below to claim a private space.\n\n"
                f"⚙️ **System Diagnostics Overview:**"
            ),
            color=COLOR_MAIN_PANEL
        )
        setup_embed.add_field(name="🛰️ System Status", value="`Online / Active`", inline=True)
        setup_embed.add_field(name="⏳ Response Window", value="`< 60 Minutes`", inline=True)
        setup_embed.add_field(name="🔒 Privacy Protocol", value="`Encrypted Tunnel`", inline=True)
        
        if interaction.guild.icon:
            setup_embed.set_thumbnail(url=interaction.guild.icon.url)
            
        setup_embed.set_footer(text=f"{interaction.guild.name} Cluster Core | {BRANDED_FOOTER}")
        
        await channel.send(embed=setup_embed, view=TicketLauncher(category_id=category.id))
        
        ok_embed = discord.Embed(description="⚙️ Support Mainframe Interface initialized and locked onto target category channels.", color=COLOR_CONFIRM_GREEN)
        await interaction.response.send_message(embed=ok_embed, ephemeral=True)

    @app_commands.command(name="ticket_add", description="Grant a user access to the ticket channel")
    @app_commands.describe(member="The target user account to add to this active ticket room")
    @app_commands.checks.has_permissions(manage_channels=True) 
    async def add_member(self, interaction: discord.Interaction, member: discord.Member):
        if not any(prefix in interaction.channel.name for prefix in ["ticket-", "billing-", "bug-"]):
            return await interaction.response.send_message("❌ Command execution context invalid: Target channel must match system tags.", ephemeral=True)
        
        await interaction.channel.set_permissions(member, read_messages=True, send_messages=True, read_message_history=True, embed_links=True, attach_files=True)
        
        embed = discord.Embed(description=f"👤 Connection established: {member.mention} has been added to this thread array.", color=COLOR_CONFIRM_GREEN)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ticket_remove", description="Revoke a user's access from the ticket channel")
    @app_commands.describe(member="The target user account to remove from this active ticket room")
    @app_commands.checks.has_permissions(manage_channels=True) 
    async def remove_member(self, interaction: discord.Interaction, member: discord.Member):
        if not any(prefix in interaction.channel.name for prefix in ["ticket-", "billing-", "bug-"]):
            return await interaction.response.send_message("❌ Command execution context invalid: Target channel must match system tags.", ephemeral=True)
        
        await interaction.channel.set_permissions(member, overwrite=None)
        
        embed = discord.Embed(description=f"👤 Connection terminated: {member.mention} has been dropped from this thread array.", color=COLOR_DANGER_RED)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ticket_rename", description="Quick-rename the channel tag prefix")
    @app_commands.describe(name="The new textual label identifier for the tail-end of the channel name string")
    @app_commands.checks.has_permissions(manage_channels=True) 
    async def rename(self, interaction: discord.Interaction, name: str):
        current_name = interaction.channel.name
        detected_prefix = None
        for prefix in ["ticket-", "billing-", "bug-"]:
            if prefix in current_name:
                detected_prefix = prefix
                break

        if not detected_prefix:
            return await interaction.response.send_message("❌ Command execution context invalid: Target channel must match system tags.", ephemeral=True)
        
        clean_name = name.lower().replace(" ", "-")
        await interaction.channel.edit(name=f"{detected_prefix}{clean_name}")
        
        embed = discord.Embed(description=f"📝 Meta update: Room designation modified to **{detected_prefix}{clean_name}**.", color=COLOR_ACTIVE_BLUE)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
