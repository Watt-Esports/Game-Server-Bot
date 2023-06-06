import os
import discord
from discord import app_commands
import paramiko
import boto3
from typing import Optional

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
SSH_USER = os.environ["SSH_USER"]
SSH_SERVER_IP = os.environ["SSH_SERVER_IP"]
SSH_PASSWORD = os.environ["SSH_PASSWORD"]

# AWS Configuration
REGION = os.environ["AWS_REGION"]
INSTANCE_ID = os.environ["EC2_INSTANCE_ID"]
MY_GUILD_OS = os.environ["MY_GUILD"]

MY_GUILD = discord.Object(id=MY_GUILD_OS)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
client.tree = app_commands.CommandTree(client)


@client.tree.command()
@app_commands.describe(script_name='The script you want to run', user='The user under whom the script will be run')
async def run(interaction: discord.Interaction, script_name: str, user: Optional[str] = None):
    """Runs a script."""
    try:
        print(f"Received command: /run {script_name} {user}")
        output, cwd = run_script(script_name, user)
        print("Sending output to Discord:")
        print(f"```\n{output}\n```")
        await interaction.response.send_message(f"Executing script in directory: `{cwd}`\n```\n{output}\n```")
    except Exception as e:
        print(f"Sending error to Discord:")
        print(f"```\nError: {str(e)}\n```")
        await interaction.response.send_message(f"```\nError: {str(e)}\n```")


@client.tree.command()
async def ec2_start(interaction: discord.Interaction):
    """Starts the EC2 instance."""
    try:
        ec2 = boto3.client("ec2", region_name=REGION)
        response = ec2.start_instances(InstanceIds=[INSTANCE_ID])
        await interaction.response.send_message(f"Starting EC2 instance `{INSTANCE_ID}`: {response}")
    except Exception as e:
        await interaction.response.send_message(f"Error starting EC2 instance: {str(e)}")


@client.tree.command()
async def ec2_stop(ctx):
    try:
        ec2 = boto3.client("ec2", region_name=REGION)
        response = ec2.stop_instances(InstanceIds=[INSTANCE_ID])
        await ctx.send(f"Stopping EC2 instance `{INSTANCE_ID}`: {response}")
    except Exception as e:
        await ctx.send(f"Error stopping EC2 instance: {str(e)}")


@client.event
async def on_ready():
    print(f'{client.user} (ID: {client.user.id}) has connected to Discord!')
    client.tree.copy_global_to(guild=MY_GUILD)
    await client.tree.sync(guild=MY_GUILD)


def run_script(script_name, user=None):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_SERVER_IP, username=SSH_USER, password=SSH_PASSWORD)

        sftp = ssh.open_sftp()
        sftp.chdir('/home/steam/')  # change directory to /home/steam/
        cwd = sftp.getcwd()  # get SFTP current working directory
        print(f"Current working directory: {cwd}")

        cmd = f"sudo -u {user} " if user else ""
        cmd += f"bash {script_name}"
        print(f"Running command: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        sftp.close()
        ssh.close()

        if error:
            print(f"Command error: {error}")
            raise Exception(error)
        else:
            print(f"Command output: {output}")
            return output, cwd

    except Exception as e:
        print(f"Error: {str(e)}")
        raise Exception(f"Error: {str(e)}")


client.run(TOKEN)