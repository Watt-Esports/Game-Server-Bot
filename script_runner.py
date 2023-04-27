import os
import discord
from discord.ext import commands
import paramiko

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
SSH_USER = os.environ["SSH_USER"]
SSH_SERVER_IP = os.environ["SSH_SERVER_IP"]
SSH_PASSWORD = os.environ["SSH_PASSWORD"]

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

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

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.command(name="run")
async def run_script_command(ctx, script_name, user=None):
    try:
        print(f"Received command: !run {script_name} {user}")
        output, cwd = run_script(script_name, user)
        print("Sending output to Discord:")
        print(f"```\n{output}\n```")
        await ctx.send(f"Executing script in directory: `{cwd}`\n```\n{output}\n```")
    except Exception as e:
        print(f"Sending error to Discord:")
        print(f"```\nError: {str(e)}\n```")
        await ctx.send(f"```\nError: {str(e)}\n```")

bot.run(TOKEN)
