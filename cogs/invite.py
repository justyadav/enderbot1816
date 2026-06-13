import discord
from discord.ext import commands
from discord import app_commands

# --- SYSTEM BRANDING CONSTANTS ---
BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"
BANNER_URL = "https://media.discordapp.net/attachments/1503357008722530377/1505483556959293628/11.png"

# Replace this with your actual Bot Invite Link from the Discord Developer Portal
BOT_INVITE_URL = "https://discord.com/oauth2/authorize?client_id=YOUR_BOT_ID_HERE&permissions=8&scope=bot%20applications.commands"


class InviteLinkButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # Add a clickable URL button directly to the view layout
        self.add_item(discord.ui.Button(
            label="Invite Ender Bot",
            url=BOT_INVITE_URL,
            style=discord.ButtonStyle.link,
            emoji="🤖"
        ))


class InviteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # INVOICE / INVITE SLASH COMMAND
    # =====================================================
    @app_commands.command(
        name="invite",
        description="Get the official secure invite link for Ender Bot X"
    )
    async def invite_bot(self, interaction: discord.Interaction):
        # Premium showoff design showcasing v2.0 capabilities
        embed = discord.Embed(
            title=f"🚀 Deploy {BOT_VERSION} to Your Server",
            description=(
                f"Bring the ultimate automation, management, and support engine to your community. "
                f"**{BOT_VERSION}** delivers high-speed operations and flawless configuration arrays.\n\n"
                f"** Why Add Ender Bot?**\n"
                f"• ⚡ **Persistent Ticket Systems:** Advanced helpdesk structures loaded directly into RAM.\n"
                f"• 🔒 **Enterprise Moderation:** Automated moderation engines built for scale.\n"
                f"• 🛰️ **24/7 Runtime Reliability:** Hosted on dedicated cloud infrastructure."
            ),
            color=discord.Color.blurple()
        )
        
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=BRANDED_FOOTER)

        # Send the response with the button block attached
        await interaction.response.send_message(embed=embed, view=InviteLinkButton())


async def setup(bot):
    await bot.add_cog(InviteCog(bot))
