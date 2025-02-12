import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os

load_dotenv(override=True)

TOKEN = os.getenv("INVITER_TOKEN")
SOURCE_GUILD_ID = int(os.getenv("SOURCE_GUILD_ID"))  
AJUDANTE_ID = int(os.getenv("AJUDANTE_ID"))
TO_BE_RECRUITED_ROLE_ID = int(os.getenv("TO_BE_RECRUITED_ROLE_ID"))
RECRUITED_ROLE_ID = int(os.getenv("RECRUITED_ROLE_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))         
RECRUITMENT_GUILD_ID = int(os.getenv("RECRUITMENT_GUILD_ID"))  
TARGET_ROLE_ID = int(os.getenv("TARGET_ROLE_ID"))              

intents = discord.Intents.default()
intents.guilds = True
intents.invites = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def has_required_role(interaction: discord.Interaction):
    user = interaction.user
    if user.guild_permissions.administrator:
        return True
    return any(role.id == AJUDANTE_ID for role in user.roles)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        print(f"Logged in as {bot.user}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="create_invite", description="Cria o Convite para o servidor principal ")
async def create_invite(interaction: discord.Interaction):
    await interaction.response.defer()
    if not has_required_role:
        await interaction.followup.send("Voce nao tem permissao para criar convite", ephemeral=True)
        return 
  
    
    source_guild = bot.get_guild(SOURCE_GUILD_ID)
    if not source_guild:
        await interaction.followup.send("Servidor Chiqueirinho nao existe", ephemeral=True)
        return

    source_channel = bot.get_channel(CHANNEL_ID)
    if not source_channel:
        await interaction.followup.send("Channel not found or no permission.", ephemeral=True)
        return

    try:
        invite = await source_channel.create_invite(max_age=86400, max_uses=1, unique=True, reason= f"O {interaction.user.name} Criou um convite")
        await interaction.followup.send(f"Aqui está o convite para o **{source_guild.name}**: {invite.url}")
    except Exception as e:
        await interaction.followup.send(f"Failed to create invite: {e}", ephemeral=True)

@bot.event
async def on_member_join(member):
    # Check if the member joined the source guild (main server)
    if member.guild.id != SOURCE_GUILD_ID:
        return

    # Get the recruitment guild
    recruitment_guild = bot.get_guild(RECRUITMENT_GUILD_ID)
    if not recruitment_guild:
        print(f"Recruitment guild {RECRUITMENT_GUILD_ID} not found.")
        return

    # Check if the user exists in the recruitment guild
    recruitment_member = recruitment_guild.get_member(member.id)
    if not recruitment_member:
        return  # User not in recruitment guild, do nothing

    # Check if user has the 'AJUDANTE' role in recruitment guild
    TO_BE_RECRUITED_ROLE = recruitment_guild.get_role(TO_BE_RECRUITED_ROLE_ID)
    if not TO_BE_RECRUITED_ROLE:
        print(f"Role Recrutado nao existe na guilda de recrutamento.")
        return

    if TO_BE_RECRUITED_ROLE_ID not in recruitment_member.roles:
        return  # User doesn't have the required role

    # Assign target role in the source guild
    target_role = member.guild.get_role(TARGET_ROLE_ID)
    if not target_role:
        print(f"Target role {TARGET_ROLE_ID} not found in source guild.")
        return

    try:
        await member.add_roles(target_role)
        print(f"Assigned role {target_role.name} to {member.display_name}")
    except discord.Forbidden:
        print(f"Bot lacks permissions to add roles in {member.guild.name}")
    except discord.HTTPException as e:
        print(f"Error adding role: {e}")

    # Update nickname to match recruitment server's display name
    try:
        await member.edit(nick=recruitment_member.display_name)
        print(f"Updated nickname for {member.display_name} to {recruitment_member.display_name}")
    except discord.Forbidden:
        print(f"Bot lacks permissions to change nickname for {member.display_name}")
    except discord.HTTPException as e:
        print(f"Error changing nickname: {e}")

    RECRUITED_ROLE = member.guild.get_role(RECRUITED_ROLE_ID)
    if not RECRUITED_ROLE:
        print(f"RECRUITED_ROLE not found in source guild.")
        return
    try:
        await recruitment_member.add_roles(RECRUITED_ROLE)
        await recruitment_member.remove_roles(TO_BE_RECRUITED_ROLE)
        print(f"Assigned role {RECRUITED_ROLE.name} to {recruitment_member.display_name}")
    except discord.Forbidden:
        print(f"Bot lacks permissions to add roles in {recruitment_member.guild.name}")
    except discord.HTTPException as e:
        print(f"Error adding role: {e}")

bot.run(TOKEN)