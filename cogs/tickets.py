import discord
from discord import app_commands
from discord.ext import commands
from database import db_manager

class DynamicTicketDropdown(discord.ui.Select):
    def __init__(self, sections):
        options = []
        for s in sections:
            options.append(discord.SelectOption(
                label=s["label"], 
                description=s["desc"], 
                emoji=s["emoji"]
            ))
        if not options:
            options.append(discord.SelectOption(label="General Support", description="Open standard request line."))

        super().__init__(placeholder="🗂️ Select Department...", min_values=1, max_values=1, custom_id="dynamic_ticket_select")

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        guild = interaction.guild
        user = interaction.user

        await interaction.response.defer(ephemeral=True)

        # Build secure, explicit permissions rules for the newly generated ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, read_message_history=True)
        }

        # Query database parameters for specific parent category allocation 
        config_collection = db_manager.get_collection("guild_settings")
        settings = await config_collection.find_one({"guild_id": guild.id}) or {}
        category_id = settings.get("ticket_category_id")
        target_category = guild.get_channel(category_id) if category_id else None

        channel_name = f"{selection.lower().replace(' ', '-')}-{user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=target_category)

        ticket_embed = discord.Embed(
            title=f"🎫 {selection} Ticket Opened",
            description=f"Hello {user.mention}, thank you for contacting **GladByte Helpdesk**.\nStaff will be with you shortly. Please explain your query in detail below.",
            color=discord.Color.from_rgb(255, 128, 0)
        )
        ticket_embed.set_footer(text="Admin Team Panel Processing")
        
        await ticket_channel.send(content=f"{user.mention} | Support Dispatch", embed=ticket_embed)
        await interaction.followup.send(f"✅ Ticket created! Access channel here: {ticket_channel.mention}", ephemeral=True)


class DynamicTicketView(discord.ui.View):
    def __init__(self, sections):
        super().__init__(timeout=None)
        self.add_item(DynamicTicketDropdown(sections))


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_collection = db_manager.get_collection("guild_settings")

    @app_commands.command(name="setup_tickets", description="Spawns the GladByte Helpdesk interactive panel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        settings = await self.config_collection.find_one({"guild_id": interaction.guild_id}) or {}
        ticket_sections = settings.get("ticket_sections", [
            {"emoji": "📌", "label": "General Support", "desc": "For general questions or server-related assistance."},
            {"emoji": "🎮", "label": "Minecraft Support", "desc": "Help with gameplay issues, bugs, or plugins."}
        ])

        desc_lines = "—————————————————————\n\n"
        for s in ticket_sections:
            desc_lines += f"{s['emoji']} **{s['label']}**\n{s['desc']}\n\n"
        desc_lines += "—————————————————————"

        embed = discord.Embed(
            title="—— GLADBYTE HELPDESK ——",
            description=desc_lines,
            color=discord.Color.from_rgb(114, 137, 218)
        )
        # Clean image linking placeholder matching original design parameters
        embed.set_image(url="https://i.imgur.com/your_banner_image.png")
        embed.set_footer(text="Made by yaduvanshi1816_")

        await interaction.response.send_message(embed=embed, view=DynamicTicketView(ticket_sections))

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
