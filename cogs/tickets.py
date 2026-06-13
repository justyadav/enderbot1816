import discord
from discord import app_commands
from discord.ext import commands
from database import db_manager
import io
import asyncio
from datetime import datetime

class TicketCloseModal(discord.ui.Modal, title="Close Support Ticket"):
    reason = discord.ui.TextInput(label="Reason for closure", placeholder="Enter closure notes...", required=True, max_length=200)

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
        await interaction.channel.set_permissions(interaction.user, read_messages=True, send_messages=True, manage_channels=True)
        button.disabled = True
        button.label = f"Claimed by {interaction.user.name}"
        await interaction.message.edit(view=self)
        await interaction.channel.send(f"💼 Ticket claimed by user assignment context: {interaction.user.mention}")


class DynamicTicketDropdown(discord.ui.Select):
    def __init__(self, sections, cog):
        self.cog = cog
        options = [discord.SelectOption(label=s["label"], description=s["desc"], emoji=s["emoji"]) for s in sections]
        if not options:
            options.append(discord.SelectOption(label="General Support", description="Standard request line."))
        super().__init__(placeholder="🗂️ Select Department...", min_values=1, max_values=1, custom_id="dynamic_ticket_select")

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        guild, user = interaction.guild, interaction.user
        await interaction.response.defer(ephemeral=True)

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
        await ticket_channel.send(content=f"{user.mention} | Helpdesk Hub", embed=ticket_embed, view=TicketControlButtons(self.cog))
        await interaction.followup.send(f"✅ Ticket deployed: {ticket_channel.mention}", ephemeral=True)


class DynamicTicketView(discord.ui.View):
    def __init__(self, sections, cog):
        super().__init__(timeout=None)
        self.add_item(DynamicTicketDropdown(sections, cog))


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_collection = db_manager.get_collection("guild_settings")

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketControlButtons(self))

    @app_commands.command(name="setup_tickets", description="Spawns the GladByte Helpdesk ticketing panel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        settings = await self.config_collection.find_one({"guild_id": interaction.guild_id}) or {}
        ticket_sections = settings.get("ticket_sections", [{"emoji": "📌", "label": "General Support", "desc": "General Assistance."}])
        banner_url = settings.get("ticket_banner_url")

        desc_lines = "—————————————————————\n\n"
        for s in ticket_sections:
            desc_lines += f"{s['emoji']} **{s['label']}**\n{s['desc']}\n\n"
        desc_lines += "—————————————————————"

        embed = discord.Embed(title="—— GLADBYTE HELPDESK ——", description=desc_lines, color=discord.Color.from_rgb(114, 137, 218))
        if banner_url: embed.set_image(url=banner_url)
        embed.set_footer(text="Made by yaduvanshi1816_")

        await interaction.response.send_message(embed=embed, view=DynamicTicketView(ticket_sections, self))

    async def process_ticket_closure(self, interaction, channel, reason):
        settings = await self.config_collection.find_one({"guild_id": channel.guild.id}) or {}
        log_channel_id = settings.get("logging_channel_id")

        await channel.send("🔒 *Archiving history and generating logs... Channel termination pending.*")

        transcript_file = None
        if settings.get("transcript_enabled", True):
            log_text = f"=== TICKET TRANSCRIPT #{channel.name} ===\nClosed By: {interaction.user.name}\nReason: {reason}\n===============================\n\n"
            async for msg in channel.history(limit=500, oldest_first=True):
                log_text += f"[{msg.created_at.strftime('%Y-%m-%d %H:%M')}] {msg.author.name}: {msg.content}\n"
            buffer = io.BytesIO(log_text.encode('utf-8'))
            transcript_file = discord.File(fp=buffer, filename=f"transcript-{channel.name}.txt")

        if log_channel_id:
            log_channel = channel.guild.get_channel(log_channel_id)
            if log_channel:
                log_embed = discord.Embed(title="🎫 Ticket Concluded", color=discord.Color.red(), timestamp=datetime.utcnow())
                log_embed.add_field(name="Target Channel", value=f"#{channel.name}", inline=True)
                log_embed.add_field(name="Executor identity", value=interaction.user.mention, inline=True)
                log_embed.add_field(name="Reason Notes", value=reason, inline=False)
                try:
                    await log_channel.send(embed=log_embed, file=transcript_file)
                except: pass

        await asyncio.sleep(3)
        await channel.delete()

    @app_commands.command(name="ticket_add", description="Adds a user to this ticket channel.")
    async def ticket_add(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Missing staff permission rules.", ephemeral=True)
            return
        await interaction.channel.set_permissions(member, read_messages=True, send_messages=True, attach_files=True)
        await interaction.response.send_message(f"✅ Granted access wrapper mapping context to: {member.mention}")

    @app_commands.command(name="ticket_remove", description="Removes a user from this ticket channel.")
    async def ticket_remove(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Missing staff permission rules.", ephemeral=True)
            return
        await interaction.channel.set_permissions(member, overwrite=None)
        await interaction.response.send_message(f"❌ Revoked access wrapper mapping context from: {member.mention}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
