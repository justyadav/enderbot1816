import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import io
import json
import os

# =========================================================
# GLOBAL CONSTANTS & HARD LOCKED GUILD BOUNDARY
# =========================================================
GUILD_ID = 1340943454934667345
TRANSCRIPT_CHANNEL_ID = 1503380993023803623
REASON_LOG_CHANNEL_ID = 1507342675244880012

BANNER_URL = "https://cdn.discordapp.com/attachments/1503380982831513701/1503418351081226250/b4ce5269-498b-41d1-8c2e-b1b02eef76e5.png"
TICKET_IMAGE_URL = "https://cdn.discordapp.com/attachments/1340943454934667345/1340943454934667345/image_449024.jpg"
SETTINGS_FILE = "ticket_settings_glad.json"

CREATOR_CREDIT = "Made by yaduvanshi1816_"


# =========================================================
# SETTINGS
# =========================================================

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Ticket Error] {e}")
            return {}
    return {}


def save_settings(data):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"[Ticket Error] {e}")


# =========================================================
# CLOSE MODAL
# =========================================================

class GladbyteCloseModal(discord.ui.Modal, title="Close Ticket"):

    reason = discord.ui.TextInput(
        label="Reason",
        style=discord.TextStyle.long,
        placeholder="Enter closing reason...",
        required=True,
        max_length=400
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        channel = interaction.channel
        guild = interaction.guild

        # =========================================
        # LOG CHANNEL
        # =========================================
        log_channel = guild.get_channel(REASON_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🔒 Ticket Closed",
                description=(
                    f"**Channel:** {channel.name}\n"
                    f"**Closed By:** {interaction.user.mention}"
                ),
                color=discord.Color.red()
            )
            embed.add_field(
                name="Reason",
                value=self.reason.value,
                inline=False
            )
            embed.set_footer(text=CREATOR_CREDIT)
            await log_channel.send(embed=embed)

        # =========================================
        # TRANSCRIPT
        # =========================================
        try:
            transcript = (
                ":envelope: ---GLADBYTE SUPPORT TRANSCRIPT---:envelope: \n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            )

            async for message in channel.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M")
                transcript += (
                    f"[{timestamp}] "
                    f"{message.author}: {message.content}\n"
                )
                if message.attachments:
                    for att in message.attachments:
                        transcript += f"Attachment: {att.url}\n"

            file_data = discord.File(
                io.BytesIO(transcript.encode()),
                filename=f"{channel.name}.txt"
            )

            transcript_channel = guild.get_channel(TRANSCRIPT_CHANNEL_ID)
            if transcript_channel:
                embed = discord.Embed(
                    title="📑 Ticket Transcript",
                    description=(
                        f"**Channel:** {channel.name}\n"
                        f"**Closed By:** {interaction.user.mention}"
                    ),
                    color=discord.Color.purple()
                )
                embed.set_footer(text=CREATOR_CREDIT)
                await transcript_channel.send(embed=embed, file=file_data)

        except Exception as e:
            print(f"Transcript Error: {e}")

        # =========================================
        # DELETE
        # =========================================
        await interaction.followup.send("🔒 Deleting ticket in 5 seconds...")
        await asyncio.sleep(5)

        try:
            await channel.delete(reason=f"Closed by {interaction.user}")
        except Exception:
            pass


# =========================================================
# BUTTONS
# =========================================================

class GladbyteControls(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    def is_staff(self, member: discord.Member):
        return (
            member.guild_permissions.manage_messages
            or member.guild_permissions.administrator
        )

    # =====================================================
    # CLAIM
    # =====================================================
    @discord.ui.button(
        label="Claim Ticket",
        style=discord.ButtonStyle.success,
        emoji="🙋",
        custom_id="glad_persistent_claim"
    )
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_staff(interaction.user):
            return await interaction.response.send_message("❌ Staff only.", ephemeral=True)

        button.disabled = True
        button.label = f"Claimed by {interaction.user.name}"
        button.style = discord.ButtonStyle.secondary

        await interaction.response.edit_message(view=self)

        embed = discord.Embed(
            description=f"✅ Ticket claimed by {interaction.user.mention}",
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=embed)

    # =====================================================
    # TRANSCRIPT
    # =====================================================
    @discord.ui.button(
        label="Transcript",
        style=discord.ButtonStyle.secondary,
        emoji="📑",
        custom_id="glad_persistent_transcript"
    )
    async def transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_staff(interaction.user):
            return await interaction.response.send_message("❌ Staff only.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        try:
            content = "GLADBYTE SUPPORT TRANSCRIPT\n\n"
            async for message in interaction.channel.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M")
                content += f"[{timestamp}] {message.author}: {message.content}\n"

            file_data = discord.File(
                io.BytesIO(content.encode()),
                filename=f"{interaction.channel.name}.txt"
            )

            log_channel = interaction.guild.get_channel(TRANSCRIPT_CHANNEL_ID)
            if log_channel:
                await log_channel.send(
                    content=f"Transcript from {interaction.channel.name}",
                    file=file_data
                )

            await interaction.followup.send("✅ Transcript saved.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error:\n```{e}```", ephemeral=True)

    # =====================================================
    # DELETE
    # =====================================================
    @discord.ui.button(
        label="Delete Ticket",
        style=discord.ButtonStyle.danger,
        emoji="🗑️",
        custom_id="glad_persistent_delete"
    )
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_staff(interaction.user):
            return await interaction.response.send_message("❌ Staff only.", ephemeral=True)

        # Repaired fallback logic handling state transfer safely to prevent interaction failures
        await interaction.response.send_modal(GladbyteCloseModal())


# =========================================================
# DROPDOWN
# =========================================================

class GladbyteDropdown(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(label="General Support", emoji="🛰️"),
            discord.SelectOption(label="Minecraft Support", emoji="🎮"),
            discord.SelectOption(label="VPS Purchase", emoji="⚡"),
            discord.SelectOption(label="Minecraft Server Purchase", emoji="🕹️"),
            discord.SelectOption(label="Partnership Support", emoji="🤝"),
            discord.SelectOption(label="Any Other", emoji="🛠️")
        ]
        super().__init__(
            placeholder="📥 Select Department",
            options=options,
            custom_id="glad_persistent_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.guild.id != GUILD_ID:
            return await interaction.response.send_message("❌ This system is locked to another server.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        # =========================================
        # LOAD CATEGORY
        # =========================================
        settings = load_settings()
        saved_cat_id = settings.get(str(guild.id))

        if not saved_cat_id:
            return await interaction.followup.send("❌ Run /setup first.", ephemeral=True)

        category = guild.get_channel(saved_cat_id)
        if category is None:
            return await interaction.followup.send("❌ Category deleted. Run /setup again.", ephemeral=True)

        # =========================================
        # ONE TICKET CHECK (BY USERNAME)
        # =========================================
        clean_name = interaction.user.name.lower().replace(" ", "-")
        channel_name = f"🎫-ticket-{clean_name}"

        existing = discord.utils.get(guild.text_channels, name=channel_name)
        if existing:
            return await interaction.followup.send(f"⚠️ You already have a ticket: {existing.mention}", ephemeral=True)

        # =========================================
        # CREATE CHANNEL
        # =========================================
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    attach_files=True,
                    embed_links=True,
                    read_message_history=True
                ),
                guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True,
                    manage_messages=True,
                    read_message_history=True
                )
            }

            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )

            await interaction.followup.send(f"✅ Ticket Created: {ticket_channel.mention}", ephemeral=True)

            # Open Embed
            opened = discord.Embed(
                title="✅ Ticket Opened",
                description=f"{interaction.user.mention} your ticket has been created.",
                color=discord.Color.green()
            )
            opened.set_footer(text=CREATOR_CREDIT)
            await ticket_channel.send(embed=opened)

            # Main Panel Embed
            embed = discord.Embed(
                title="🏢 Gladbyte Helpdesk",
                description=(
                    f"👋 Welcome {interaction.user.mention}\n\n"
                    f"🛠️ Department: **{self.values[0]}**\n\n"
                    f"Please explain your issue below."
                ),
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=TICKET_IMAGE_URL)
            embed.set_footer(text=CREATOR_CREDIT)

            await ticket_channel.send(embed=embed, view=GladbyteControls())

        except Exception as e:
            await interaction.followup.send(f"❌ Error:\n```{e}```", ephemeral=True)


# =========================================================
# VIEW
# =========================================================

class GladbyteView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GladbyteDropdown())


# =========================================================
# COG
# =========================================================

class GladbyteTickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # Fixed registration strategy to ensure persistence even across late runtime cog loads
        self.bot.loop.create_task(self.register_persistent_elements())

    async def register_persistent_elements(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(GladbyteView())
        self.bot.add_view(GladbyteControls())

    def is_staff(self, interaction: discord.Interaction):
        return (
            interaction.user.guild_permissions.manage_messages
            or interaction.user.guild_permissions.administrator
        )

    # =====================================================
    # SETUP PANEL COMMAND
    # =====================================================
    @app_commands.command(
        name="setup",
        description="Setup Ticket System"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_panel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        category: discord.CategoryChannel
    ):
        if interaction.guild.id != GUILD_ID:
            return await interaction.response.send_message("❌ Wrong server.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        settings = load_settings()
        settings[str(interaction.guild.id)] = category.id
        save_settings(settings)

        embed = discord.Embed(
            title=" ━━━ GLADBYTE HELPDESK ━━━ ",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🛰️ **General Support**\n"
                "For general questions or server-related assistance.\n\n"
                "🎮 **Minecraft Support**\n"
                "Help with gameplay issues, bugs, or plugins.\n\n"
                "⚡ **VPS Purchase**\n"
                "Know about our Virtual Private Servers.\n\n"
                "🕹️ **Minecraft Server Purchase**\n"
                "Create a Ticket here to Purchase Minecraft Servers.\n\n"
                "🤝 **Partnership Support**\n"
                "Questions about partnerships or collaborations.\n\n"
                "🛠️ **Any Other**\n"
                "Create a Ticket Under this Category for Any Other Query.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.purple()
        )
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=CREATOR_CREDIT)

        await channel.send(embed=embed, view=GladbyteView())
        await interaction.followup.send("✅ Ticket system setup complete.", ephemeral=True)

    # =====================================================
    # ADD USER COMMAND
    # =====================================================
    @app_commands.command(
        name="gadd",
        description="Add user to ticket"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def add_user(self, interaction: discord.Interaction, member: discord.Member):
        if not self.is_staff(interaction):
            return await interaction.response.send_message("❌ Staff only.", ephemeral=True)

        if not interaction.channel.name.startswith("🎫-ticket-"):
            return await interaction.response.send_message("❌ Not a valid ticket channel.", ephemeral=True)

        await interaction.channel.set_permissions(
            member,
            view_channel=True,
            send_messages=True,
            attach_files=True,
            embed_links=True
        )
        await interaction.response.send_message(f"✅ Added {member.mention} to the ticket.")

    # =====================================================
    # REMOVE USER COMMAND
    # =====================================================
    @app_commands.command(
        name="gremove",
        description="Remove user from ticket"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def remove_user(self, interaction: discord.Interaction, member: discord.Member):
        if not self.is_staff(interaction):
            return await interaction.response.send_message("❌ Staff only.", ephemeral=True)

        if not interaction.channel.name.startswith("🎫-ticket-"):
            return await interaction.response.send_message("❌ Not a valid ticket channel.", ephemeral=True)

        await interaction.channel.set_permissions(member, overwrite=None)
        await interaction.response.send_message(f"✅ Removed {member.mention} from the ticket.")


# =========================================================
# REGISTRATION COG INITIALIZER
# =========================================================

async def setup(bot):
    await bot.add_cog(GladbyteTickets(bot))