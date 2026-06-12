import discord
from discord import app_commands
from discord.ext import commands

class TicketControlView(discord.ui.View):
    """View handling the archival closure step within a live ticket channel."""
    def __init__(self):
        super().__init__(timeout=None) # Explicitly persistent layout runtime parameter

    @discord.ui.button(label="Close Operational Ticket", style=discord.ButtonStyle.red, custom_id="persistent_bot:ticket:close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Commencing channel evaluation archival tracking. This channel will close shortly...")
        # Asynchronously execute destruction delay cleanly
        await interaction.channel.delete(reason="Ticket closed by operational target user request.")

class TicketCreationHub(discord.ui.View):
    """View displayed in the server channel where users click to open a ticket."""
    def __init__(self):
        super().__init__(timeout=None) # Infinite preservation lifecycle parameter

    @discord.ui.button(label="📩 Initialize Ticket Creation", style=discord.ButtonStyle.blurple, custom_id="persistent_bot:ticket:create")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # Scan for existing ticket channel instances for this user
        sanitized_username = user.name.lower().replace(" ", "-")
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{sanitized_username}")
        
        if existing_channel:
            return await interaction.response.send_message(f"❌ Aborted: You already possess an unresolved active service matrix interface open here: {existing_channel.mention}", ephemeral=True)

        await interaction.response.defer(ephemeral=True, thinking=True)

        # Enforce highly strict visibility policies restricted to system personnel and the opener
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True, manage_channels=True)
        }

        # Issue create instruction
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            overwrites=overwrites,
            topic=f"Dedicated private service record channel generated for individual {user.name} (ID: {user.id})"
        )

        # Send introductory greeting paired with interactive closure controller dashboard 
        embed = discord.Embed(
            title="🎫 Support Desk Framework Active",
            description=f"Welcome {user.mention}. Describe your issue clearly. Support staff will assist you shortly.",
            color=discord.Color.teal()
        )
        await ticket_channel.send(embed=embed, view=TicketControlView())
        await interaction.followup.send(f"✅ Your secure ticket terminal channel has been provisioned: {ticket_channel.mention}", ephemeral=True)


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Register persistent views globally to catch interactions across bot restarts
        self.bot.add_view(TicketCreationHub())
        self.bot.add_view(TicketControlView())

    @app_commands.command(name="ticket-setup", description="Deploy the persistent interactive ticketing interface panel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_setup(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎟️ Core Operations Support Center",
            description="If you require direct administrative assistance or need to file a formal request, select the interactive route tracking link below.",
            color=discord.Color.dark_grey()
        )
        # Drop persistent interaction elements mapped inside self-repair setup loops
        await interaction.response.send_message("Deploying dynamic ticket layout interface matrix...", ephemeral=True)
        await interaction.channel.send(embed=embed, view=TicketCreationHub())

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))