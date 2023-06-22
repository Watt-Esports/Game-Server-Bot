import paramiko
from exceptions import CommandError


class SSHModule:
    def __init__(self, user, ip, password, home_directory):
        self.user = user
        self.ip = ip
        self.password = password
        self.home_directory = home_directory

    def run_script(self, script_name, user=None):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, username=self.user, password=self.password)

            sftp = ssh.open_sftp()
            sftp.chdir(self.home_directory)  # change directory to home_directory
            cwd = sftp.getcwd()  # get SFTP current working directory

            cmd = f"sudo -u {user} " if user else ""
            cmd += f"bash {script_name}"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            sftp.close()
            ssh.close()

            if error:
                raise CommandError(error)

            return output, cwd
        except Exception as e:
            raise CommandError(str(e))
