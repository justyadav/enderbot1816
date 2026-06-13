import discord
from discord import app_commands
from discord.ext import commands
from database import db_manager
import io
import asyncio
from datetime import datetime

class TicketCloseModal(discord.ui.Modal, title="Close Support Ticket"):
    reason = discord.ui.TextInput(
        label="Reason for closure", 
        placeholder="e.g., Issue resolved / User inactive", 
        required=True, 
        max_length=200
    )

    def __init__(self, cog, channel):
        super().__init__()
        self.cog = cog
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.cog.process_ticket_closure(interaction, self.channel, self.reason.value)


class TicketControlButtons(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="btn_close_ticket")
    async def close_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        settings = await self.cog.config_collection.find_one({"guild_id": interaction.guild_id}) or {}
        
        # Check if dashboard requires an official text reason modal popup
        if settings.get("close_reason_enabled", True):
            await interaction.response.send_modal(TicketCloseModal(self.cog, interaction.channel))
        else:
            await interaction.response.defer()
            await self.cog.process_ticket_closure(interaction, interaction.channel, "No closure reason specified.")

    @discord.ui.button(label="🙋 Claim Ticket", style=discord.ButtonStyle.success, custom_id="btn_claim_ticket")
    async def claim_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Authorized support team access only.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        # Adjust overrides so the claiming staff member has elevated permissions inside this channel
        await interaction.channel.set_permissions(interaction.user, read_messages=True, send_messages=True, manage_channels=True)
        
        # Disable the claim button interaction globally across caches
        button.disabled = True
        button.label = f"Claimed by {interaction.user.name}"
        await interaction.message.edit(view=self)
        
        await interaction.channel.send(f"💼 This ticket has been claimed by {interaction.user.mention}.")


class DynamicTicketDropdown(discord.ui.Select):
    def __init__(self, sections, cog):
        self.cog = cog
        
        # 🛡️ AIRTIGHT GUARD 1: Failsafe fallback right inside the constructor loop
        if not sections or len(sections) == 0:
            sections = [{"emoji": "📌", "label": "General Support", "desc": "Standard general assistance query lines."}]
            
        options = [
            discord.SelectOption(label=s["label"], description=s["desc"], emoji=s["emoji"]) 
            for s in sections
        ]
        
        super().__init__(
            placeholder="🗂️ Select Department...", 
            min_values=1, 
            max_values=1, 
            custom_id="dynamic_ticket_select",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        guild = interaction.guild
        user = interaction.user
        await interaction.response.defer(ephemeral=True)

        # Restrict standard permissions to hide this text channel from regular server members
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, read_message_history=True)
        }

        settings = await self.cog.config_collection.find_one({"guild_id": guild.id}) or {}
        category_id = settings.get("ticket_category_id")
        target_category = guild.get_channel(category_id) if category_id else None

        channel_name = f"{selection.lower().replace(' ', '-')}-{user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=target_category)

        ticket_embed = discord.Embed(
            title=f"🎫 {selection} Ticket Opened",
            description=f"Hello {user.mention}, thank you for contacting **GladByte Helpdesk**.\nPlease describe your request. A staff member will be with you shortly.",
            color=discord.Color.orange()
        )
        
        # Anchor persistent internal buttons right below the initialization greetings card
        await ticket_channel.send(content=f"{user.mention} | Support Pipeline", embed=ticket_embed, view=TicketControlButtons(self.cog))
        await interaction.followup.send(f"✅ Ticket deployed! Channel link: {ticket_channel.mention}", ephemeral=True)


class DynamicTicketView(discord.ui.View):
    def __init__(self, sections, cog):
        super().__init__(timeout=None)
        
        # 🛡️ AIRTIGHT GUARD 2: Force a fallback array here as well just in case
        if not sections or len(sections) == 0:
            sections = [{"emoji": "📌", "label": "General Support", "desc": "Standard general assistance query lines."}]
            
        self.add_item(DynamicTicketDropdown(sections, cog))


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_collection = db_manager.get_collection("guild_settings")

    @commands.Cog.listener()
    async def on_ready(self):
        # Register view listener persistently to preserve button states when bot reboots
        self.bot.add_view(TicketControlButtons(self))

    @app_commands.command(name="setup_tickets", description="Spawns the GladByte Helpdesk ticketing panel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        settings = await self.config_collection.find_one({"guild_id": interaction.guild_id}) or {}
        
        # 🛡️ AIRTIGHT GUARD 3: Fallback safety net inside the command logic
        ticket_sections = settings.get("ticket_sections")
        if not ticket_sections or len(ticket_sections) == 0:
            ticket_sections = [
                {"emoji": "📌", "label": "General Support", "desc": "Standard general assistance query lines."}
            ]
            
        banner_url = settings.get("ticket_banner_url")

        desc_lines = "—————————————————————\n\n"
        for s in ticket_sections:
            desc_lines += f"{s['emoji']} **{s['label']}**\n{s['desc']}\n\n"
        desc_lines += "—————————————————————"

        embed = discord.Embed(
            title="—— GLADBYTE HELPDESK ——", 
            description=desc_lines, 
            color=discord.Color.from_rgb(114, 137, 218)
        )
        if banner_url: 
            embed.set_image(url=banner_url)
        embed.set_footer(text="Made by yaduvanshi1816_")

        await interaction.response.send_message(embed=embed, view=DynamicTicketView(ticket_sections, self))

    async def process_ticket_closure(self, interaction, channel, reason):
        settings = await self.config_collection.find_one({"guild_id": channel.guild.id}) or {}
        log_channel_id = settings.get("logging_channel_id")

        await channel.send("🔒 *Archiving history and generating logs... Channel termination pending.*")

        # Compile and generate a text transcript file if allowed by dashboard configuration
        transcript_file = None
        if settings.get("transcript_enabled", True):
            log_text = f"=== GLADBYTE TICKET TRANSCRIPT #{channel.name} ===\n"
            log_text += f"Closed By: {interaction.user.name} ({interaction.user.id})\n"
            log_text += f"Reason: {reason}\n"
            log_text += f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            log_text += "====================================================\n\n"
            
            async for msg in channel.history(limit=500, oldest_first=True):
                log_text += f"[{msg.created_at.strftime('%Y-%m-%d %H:%M')}] {msg.author.name}: {msg.content}\n"
                if msg.attachments:
                    for att in msg.attachments:
                        log_text += f" -> Attachment URL: {att.url}\n"
                        
            buffer = io.BytesIO(log_text.encode('utf-8'))
            transcript_file = discord.File(fp=buffer, filename=f"transcript-{channel.name}.txt")

        # Forward moderation details accompanied with the compiled transcript directly to logs channel
        if log_channel_id:
            log_channel = channel.guild.get_channel(log_channel_id)
            if log_channel:
                log_embed = discord.Embed(
                    title="🎫 Ticket Concluded & Logged", 
                    color=discord.Color.red(), 
                    timestamp=datetime.utcnow()
                )
                log_embed.add_field(name="Target Channel", value=f"#{channel.name}", inline=True)
                log_embed.add_field(name="Closed By", value=interaction.user.mention, inline=True)
                log_embed.add_field(name="Reason Notes", value=reason, inline=False)
                try:
                    if transcript_file:
                        await log_channel.send(embed=log_embed, file=transcript_file)
                    else:
                        await log_channel.send(embed=log_embed)
                except: 
                    pass

        # Conclude operations and delete the text channel
        await asyncio.sleep(3)
        await channel.delete(reason=f"Ticket closed by {interaction.user.name}: {reason}")

    # Slash Command: /ticket_add <user>
    @app_commands.command(name="ticket_add", description="Adds a user to this ticket channel.")
    @app_commands.describe(member="The user you want to add to this ticket channel.")
    async def ticket_add(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Missing staff permission rules.", ephemeral=True)
            return
        await interaction.channel.set_permissions(member, read_messages=True, send_messages=True, attach_files=True)
        await interaction.response.send_message(f"✅ Granted ticket access mapping view context to: {member.mention}")

    # Slash Command: /ticket_remove <user>
    @app_commands.command(name="ticket_remove", description="Removes a user from this ticket channel.")
    @app_commands.describe(member="The user you want to remove from this ticket channel.")
    async def ticket_remove(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Missing staff permission rules.", ephemeral=True)
            return
        await interaction.channel.set_permissions(member, overwrite=None)
        await interaction.response.send_message(f"❌ Revoked ticket access mapping view context from: {member.mention}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
