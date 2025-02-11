import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os

load_dotenv(override=True)

TOKEN = os.getenv("INVITER_TOKEN")
SOURCE_GUILD_ID = int(os.getenv("SOURCE_GUILD_ID"))
AJUDANTE_ID = int(os.getenv("AJUDANTE_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
# Bot setup with required intents
intents = discord.Intents.default()
intents.guilds = True
intents.invites = True

bot = commands.Bot(command_prefix="!", intents=intents)

def has_required_role(interaction: discord.Interaction):
    """Validation function to check if a user has the required role or is an admin"""
    user = interaction.user
    if user.guild_permissions.administrator:  # Allow server admins
        return True

    # Check if the user has the required role
    for role in user.roles:
        if role.id == AJUDANTE_ID:
            return True
    
    return False
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()  # Sync slash commands
        print(f"Synced {len(synced)} command(s)")
        print(f"Logged in as {bot.user}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="create_invite", description="Create an invite from another server")
async def create_invite(interaction: discord.Interaction):
    """Slash command to create an invite and send it in the invoked channel"""
    source_guild = bot.get_guild(SOURCE_GUILD_ID)

    if not source_guild:
        await interaction.response.send_message("I am not in the source server.", ephemeral=True)
        return

    # Find a channel in the source server where the bot can create invites
    source_channel = bot.get_channel(CHANNEL_ID)
    if not source_channel:
        await interaction.response.send_message("I don't have permission to create invites in any channel.", ephemeral=True)
        return

    # Create an invite with 1 max use
    invite = await source_channel.create_invite(max_age=86.400,max_uses=1, unique=True)

    # Send the invite to the same channel where the command was invoked
    await interaction.response.send_message(f"Aqui está o convite para o **{source_guild.name}**: {invite.url}")

# Run the bot
bot.run(TOKEN)
