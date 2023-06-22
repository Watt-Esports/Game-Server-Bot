# main.py
import os
import discord
from discord import app_commands, Embed
from typing import Optional
import logging
from exceptions import CommandError, EC2Error
from ssh_module import SSHModule
from ec2_module import EC2Module

# Environment Variables with Default Values
TOKEN = os.getenv("DISCORD_BOT_TOKEN", "default_token")
SSH_USER = os.getenv("SSH_USER", "default_user")
SSH_SERVER_IP = os.getenv("SSH_SERVER_IP", "default_ip")
SSH_PASSWORD = os.getenv("SSH_PASSWORD", "default_password")
HOME_DIRECTORY = os.getenv("HOME_DIRECTORY", "/home/steam/")
REGION = os.getenv("AWS_REGION", "default_region")
INSTANCE_ID = os.getenv("EC2_INSTANCE_ID", "default_instance_id")
MY_GUILD_OS = os.getenv("MY_GUILD", "default_guild")

MY_GUILD = discord.Object(id=MY_GUILD_OS)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
client.tree = app_commands.CommandTree(client)

# Set up logging
logging.basicConfig(level=logging.INFO)

ssh = SSHModule(SSH_USER, SSH_SERVER_IP, SSH_PASSWORD, HOME_DIRECTORY)
ec2 = EC2Module(REGION, INSTANCE_ID)

@client.tree.command()
@app_commands.describe(script_name='The script you want to run', user='The user under whom the script will be run')
async def run(interaction: discord.Interaction, script_name: str, user: Optional[str] = None):
    """Runs a script."""
    try:
        logging.info(f"Received command: /run {script_name} {user}")
        output, cwd = ssh.run_script(script_name, user)
        logging.info("Sending output to Discord:")
        logging.info(f"```\n{output}\n```")
        embed = Embed(title="Script Execution", description=f"Executing script in directory: `{cwd}`", color=0x00ff00)
        embed.add_field(name="Output", value=f"```\n{output}\n```", inline=False)
        await interaction.response.send_message(embed=embed)
    except CommandError as e:
        logging.error(f"Sending error to Discord:")
        logging.error(f"```\nError: {str(e)}\n```")
        embed = Embed(title="Error", description=f"```\nError: {str(e)}\n```", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@client.tree.command()
async def ec2_start(interaction: discord.Interaction):
    """Starts the EC2 instance."""
    try:
        response = ec2.start_instance()
        embed = Embed(title="EC2 Instance Start", description=f"Starting EC2 instance `{INSTANCE_ID}`: {response}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except EC2Error as e:
        embed = Embed(title="Error", description=f"Error starting EC2 instance: {str(e)}", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@client.tree.command()
async def ec2_stop(interaction: discord.Interaction):
    """Stops the EC2 instance."""
    try:
        response = ec2.stop_instance()
        embed = Embed(title="EC2 Instance Stop", description=f"Stopping EC2 instance `{INSTANCE_ID}`: {response}", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
    except EC2Error as e:
        embed = Embed(title="Error", description=f"Error stopping EC2 instance: {str(e)}", color=0xff0000)
        await interaction.response.send_message(embed=embed)

@client.event
async def on_ready():
    logging.info(f'{client.user} (ID: {client.user.id}) has connected to Discord!')
    client.tree.copy_global_to(guild=MY_GUILD)
    await client.tree.sync(guild=MY_GUILD)

client.run(TOKEN)
