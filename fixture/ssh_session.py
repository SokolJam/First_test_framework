import paramiko
import logging
import constants

client = paramiko.SSHClient()


class SSHSession(object):
    """
    THe class is used for create SSH connect, send command from SSH and close SSH-session.
    Include staticmethods: ssh_connect, ssh_command and ssh_close.
    """

    @staticmethod
    def ssh_connect():
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        logging.info('Connect to client-host = {}'.format(constants.HOST_CLIENT))
        client.connect(hostname=constants.HOST_CLIENT)

    @staticmethod
    def ssh_command(cmd):
        """
        The class method for send commands from SSH-connect.
        :param cmd: str
        :return: stdin, stdout, stderr, exit_code of command
        """
        stdin, stdout, stderr = client.exec_command(cmd)
        exit_ = stdout.channel.recv_exit_status()
        return stdin, stdout, stderr, exit_

    @staticmethod
    def ssh_close():
        logging.info('Disconnect to client-host = {}'.format(constants.HOST_CLIENT))
        client.close()