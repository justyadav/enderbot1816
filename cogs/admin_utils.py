import discord
from discord import app_commands
from discord.ext import commands
import time
import asyncio

# --- SYSTEM BRANDING CONSTANTS ---
BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"
BANNER_URL = "https://media.discordapp.net/attachments/1503357008722530377/1505483556959293628/11.png"

COLOR_PRIMARY = discord.Color.blurple()
COLOR_SUCCESS = discord.Color.green()
COLOR_WARNING = discord.Color.from_rgb(255, 191, 0)
COLOR_DANGER = discord.Color.red()
COLOR_DARK = discord.Color.from_rgb(34, 36, 41)


class AdminUtilsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # =====================================================
    # MODERATION: /BAN
    # =====================================================
    @app_commands.command(name="ban", description="Permanently bans a disruptive target from the server matrix")
    @app_commands.describe(member="The user to ban", reason="The administrative reason for the ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_user(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No administrative reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ **Operation Aborted:** Target individual possesses equal or superior role authority.", ephemeral=True)
        
        await interaction.response.defer()
        
        # Try sending a notification direct message to the user before the ban
        try:
            dm_embed = discord.Embed(
                title=f"🔨 Prohibited Action Notice ─── {interaction.guild.name}",
                description=f"Your terminal clearance has been revoked from our server infrastructure.\n\n**Reason:** {reason}",
                color=COLOR_DANGER
            )
            dm_embed.set_footer(text=BRANDED_FOOTER)
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            pass

        await member.ban(reason=f"Executed by {interaction.user.name} | Reason: {reason}")
        
        embed = discord.Embed(
            title="🔨 Target Ban Terminated Successfully",
            description=f"**User Account:** {member.mention} (`{member.id}`)\n**Enforcing Executive:** {interaction.user.mention}\n**Reasoning:** {reason}",
            color=COLOR_DANGER,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=BRANDED_FOOTER)
        await interaction.followup.send(embed=embed)

    # =====================================================
    # MODERATION: /TIMEOUT
    # =====================================================
    @app_commands.command(name="timeout", description="Temporarily isolates a user into communication silence")
    @app_commands.describe(member="The user to mute", minutes="Duration of the restriction in minutes", reason="Administrative reason")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout_user(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No administrative reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ **Operation Aborted:** Target individual possesses equal or superior role authority.", ephemeral=True)
        
        await interaction.response.defer()
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=f"Executed by {interaction.user.name} | {reason}")

        embed = discord.Embed(
            title="⏳ Communication Line Isolated",
            description=f"**User Account:** {member.mention}\n**Duration Bound:** `{minutes} Minutes`\n**Enforcing Executive:** {interaction.user.mention}\n**Reasoning:** {reason}",
            color=COLOR_WARNING,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=BRANDED_FOOTER)
        await interaction.followup.send(embed=embed)

    # =====================================================
    # UTILITY: /UPTIME
    # =====================================================
    @app_commands.command(name="uptime", description="Check the running core online duration stats")
    async def get_uptime(self, interaction: discord.Interaction):
        uptime_seconds = int(time.time() - self.start_time)
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed = discord.Embed(
            title=f"⏳ {BOT_VERSION} Core Online Status",
            description=f"Operational continuity map: `{days}d {hours}h {minutes}m {seconds}s` without execution interruption.",
            color=COLOR_PRIMARY
        )
        embed.set_footer(text=BRANDED_FOOTER)
        await interaction.response.send_message(embed=embed)

    # =====================================================
    # INFORMATION: /SERVERINFO
    # =====================================================
    @app_commands.command(name="serverinfo", description="Exposes deep diagnostic and demographic metrics of this server guild")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"🌐 Server Infrastructure Profile: {guild.name}",
            color=COLOR_DARK,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="🆔 Guild Reference ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="👑 Founding Owner", value=f"{guild.owner.mention}", inline=True)
        embed.add_field(name="📅 Created On", value=f"<t:{int(guild.created_at.timestamp())}:D>", inline=True)
        embed.add_field(name="👥 Population Core", value=f"`{guild.member_count:,} total users`", inline=True)
        embed.add_field(name="📁 Channel Count", value=f"`{len(guild.channels)} Total Layers`", inline=True)
        embed.add_field(name="✨ Premium Tier Boosts", value=f"`Tier {guild.premium_tier} ({guild.premium_subscription_count} Boosts)`", inline=True)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=BRANDED_FOOTER)
        await interaction.response.send_message(embed=embed)

    # =====================================================
    # INFORMATION: /USERINFO
    # =====================================================
    @app_commands.command(name="userinfo", description="Exposes public database analytics for a verified server individual")
    @app_commands.describe(member="Target account to inspect")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        roles = [role.mention for role in member.roles[1:]]  # Filter out @everyone
        roles_display = ", ".join(roles) if roles else "`No Roles Assigned`"

        embed = discord.Embed(
            title=f"👤 Security Profile Mapping: {member.display_name}",
            color=COLOR_PRIMARY,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="🏷️ Tag Identity", value=f"`{member.name}`", inline=True)
        embed.add_field(name="🆔 Global Database ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="🤖 Bot System Flag", value=f"`{member.bot}`", inline=True)
        embed.add_field(name="📅 Account Sparked", value=f"<t:{int(member.created_at.timestamp())}:D>", inline=True)
        embed.add_field(name="📥 Guild Induction", value=f"<t:{int(member.joined_at.timestamp())}:D>", inline=True)
        embed.add_field(name="🔱 Key Privilege Role", value=member.top_role.mention, inline=True)
        embed.add_field(name="🛡️ Identity Badges / Roles", value=roles_display, inline=False)

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=BRANDED_FOOTER)
        await interaction.response.send_message(embed=embed)

    # =====================================================
    # PRUNING: /CLEAR
    # =====================================================
    @app_commands.command(name="clear", description="Bulk purges a specific number of logs/messages from the channel frame")
    @app_commands.describe(amount="Quantity of lines to instantly wipe out")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_messages(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            return await interaction.response.send_message("❌ **Operational Bound Error:** You can only purge between `1` and `100` logs concurrently.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        purged = await interaction.channel.purge(limit=amount)
        
        embed = discord.Embed(
            description=f"🗑️ **Pruning Cycle Terminated:** Successfully destroyed `{len(purged)}` message payloads from memory array.",
            color=COLOR_SUCCESS
        )
        embed.set_footer(text=BRANDED_FOOTER)
        await interaction.followup.send(embed=embed, ephemeral=True)

    # =====================================================
    # MAINTENANCE: /NUKE
    # =====================================================
    @app_commands.command(name="nuke", description="Completely purges and clones the current channel space to wipe clean historical records")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def nuke_channel(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        channel = interaction.channel
        # Clone structural settings exactly
        new_channel = await channel.clone(reason=f"Nuke sequence initiated by {interaction.user.name}")
        await new_channel.edit(position=channel.position)
        
        # Vaporize the old layout
        await channel.delete(reason="Channel space wiped completely via v2.0 core")

        embed = discord.Embed(
            title="💥 Mainframe Nuke Cycle Concluded",
            description="This channel room has been completely split-cloned and vaporized to erase trace structures.",
            color=COLOR_DANGER
        )
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=BRANDED_FOOTER)
        await new_channel.send(embed=embed)

    # =====================================================
    # MAINTENANCE: /DELETE
    # =====================================================
    @app_commands.command(name="delete", description="Permanently destroys the current channel or target text channel layer")
    @app_commands.describe(target_channel="Optional target channel to delete. Defaults to the current active text channel.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def delete_channel(self, interaction: discord.Interaction, target_channel: discord.TextChannel = None):
        target = target_channel or interaction.channel
        
        # If deleting the current channel, send a notice before it shuts down
        if target == interaction.channel:
            await interaction.response.send_message("⚙️ **Terminating channel layer map immediately...**")
            await asyncio.sleep(1.5)
            await target.delete(reason=f"Deconstruct sequence authorized by {interaction.user.name}")
        else:
            await target.delete(reason=f"Deconstruct sequence authorized by {interaction.user.name}")
            embed = discord.Embed(
                description=f"🗑️ Successfully destroyed and deleted channel layout layer: **#{target.name}**.",
                color=COLOR_SUCCESS
            )
            embed.set_footer(text=BRANDED_FOOTER)
            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminUtilsCog(bot))
