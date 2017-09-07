import logging
import subprocess

import os
import sys

import constants
from fixture.ssh_session import SSHSession


def check_and_log(fn):
    """
    The decorator for functions, which has a parameter string like a command.
    There is check a condition every of commands and logs everyone what doing this one.

    :param fn:
    :return: result of doing the command, success or not - True or False
    and stdout after execute of command    """
    def wrapper(command):
        try:
            result_of_command = fn(command)
            if result_of_command.is_success:
                logging.info('{} - Done'.format(command))
            else:
                logging.error('{} - FAIL ({})'.format(command, result_of_command.err))
        except SystemError:
            logging.exception('Something was wrong with system!')
            print('''You have SystemError!
                  File with logs you can reed in {}'''.format(os.path.abspath(constants.NAME_LOG_FILE)))
            sys.exit()
        return result_of_command.is_success, result_of_command.out
    return wrapper


@check_and_log
def command_on_server(cmd):
    """
    The function handle of commands for server, check of command is instance the string type, doing and return result.
    :param cmd:
    :return: success or not - True or False
    """
    assert isinstance(cmd, str)
    command = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = command.communicate()
    exit_ = command.returncode
    resp = Response(out, err, exit_)
    return resp


@check_and_log
def command_on_client(cmd):
    """
    The function handle of commands for client, check of command is instance the string type, doing from SSH session
    and return result. But this function does not connect from SSH.
    :param cmd:
    :return: object of Class "Response" with bool value True or False, which depends on result of command
    - success or not.
    """
    assert isinstance(cmd, str)
    stdin, stdout, stderr, exit_ = SSHSession.ssh_command(cmd)
    out = stdout.readline()
    resp = Response(out, stderr, exit_)
    return resp


class Response(object):
    """
    The class got input stdout, stderr and exit_code of result of command.
    """

    def __init__(self, out, err, exit_):
        self.out = out
        self.err = err
        self.exit = exit_

    @property
    def is_success(self):
        """
        The method of class which in depends on input data determines the success of command or not.
        :return: True of False
        """
        if self.err != constants.STDERR_EMPTY and self.exit != constants.EXIT_SUCCESS:
            return False
        else:
            return True


class Commands(object):
    """
    The base class of commands often used  in a Test Framework. Every of the methods log the actions they perform.
    """

    def __init__(self):
        self.machines = {'server': command_on_server, 'client': command_on_client}

    def check_nfs(self, client_server):
        """
        The method of class checks to install NFS-package on the machine (server or client)
        in depends of value parameter.
        :param client_server: have a value 'server' or 'client'
        :return: True or False
        """
        logging.info('Check by install nfs-utils on {}'.format(client_server))
        check = self.machines[client_server]('rpm -q nfs-utils')
        return check

    def cmd_install_nfs(self, client_server):
        """
        The method of class installs NFS-package on the machine (server or client)
        in depends of value parameter.
        :param client_server: have a value 'server' or 'client'
        :return:
        """
        logging.info('Install nfs-utils on {}'.format(client_server))
        self.machines[client_server]('yum install -y nfs-utils')

    def service_on(self, client_server):
        """
        The method of class switches on services of NFS on the machine (server or client)
        in depends of value parameter.
        :param client_server: have a value 'server' or 'client'
        :return:
        """
        logging.info('Start services of NFS-{}'.format(client_server))
        for service in constants.SERVICES:
            self.machines[client_server]('systemctl enable ' + service)
            self.machines[client_server]('systemctl start ' + service)

    def make_file(self, client_server, path):
        """
        The method of class makes a test file on the machine (server or client)
        in depends of value parameter.
        :param client_server: have a value 'server' or 'client'
        :param path: full path include file-name in the string type.
        :return: True or False
        """
        logging.info('Create test-file on {}'.format(client_server))
        result = self.machines[client_server]('echo Test_message {}'.format(path))
        return result

    def make_dir(self, client_server, path):
        """
        The method of class make a directory on the machine (server or client)
        in depends of value parameter.
        :param client_server: have a value 'server' or 'client'
        :param path: full path include directory-name in the string type.
        :return:
        """
        logging.info('Make nfs share directory')
        self.machines[client_server]('mkdir {}'.format(path))
        os.chmod(path, 0777)

    def remove(self, client_server, path, file_or_directory='file'):
        """
        The method of class removes a file or directory on the machine (server or client)
        in depends of value parameter.
        :param client_server: have a value 'server' or 'client'
        :param path: full path include name of file or directory in the string type.
        :param file_or_directory: have a value 'file' or 'directory', default value is "file"
        :return:
        """

        logging.info('Remove {} from {}'.format(file_or_directory, client_server))
        if file_or_directory == 'file':
            self.machines[client_server]('rm -f {}'.format(path))
        elif file_or_directory == 'directory':
            self.machines[client_server]('rm -rf {}'.format(path))
        else:
            raise NameError

    def restart_nfs_server(self):
        """
        The method of class restarts NFS-server on the server's machine.
        :return:
        """
        logging.info('Restart nfs-server')
        command_on_server('systemctl restart nfs-server')

    def clean_export_file(self):
        """
        The method of class cleans the file "exports" which contain information about ip client and properties of
        access on the server's machine.
        :return:
        """
        logging.info('Clean /etc/exports')
        command_on_server('cat /dev/null > /etc/exports')

    def change_firewall_ports(self):
        """
        The method of class assigns access port for Firewall on the server.
        :return:
        """
        logging.info('Change settings of server\'s firewall')
        for port in constants.FIREWALL_PORTS:
            command_on_server('firewall-cmd --permanent --add-port={}/tcp'.format(port))
        command_on_server('firewall-cmd --reload')

    def mount_nfs_share(self, host_server, share_name_server, share_name_client):
        """
        The method of class mounts share directory on the client.
        :param host_server: str include IP of server
        :param share_name_server: full path include the name of share directory of server (str)
        :param share_name_client: full path include the name of share directory of client (str)
        :return:
        """
        logging.info('Mounted share directory for client')
        command_on_client('mount -t nfs {}:{} {}'.format(host_server, share_name_server, share_name_client))

    def umount_nfs_share(self, share_name_client):
        """
        The method of class dismounts share directory on the client.
        :param share_name_client: full path include the name of share directory of client (str)
        :return:
        """
        logging.info('Unmounted share directory for client')
        command_on_client('umount {}'.format(share_name_client))

    def search_text_in_file(self, client_server, text, path):
        """
        The method of class searches pattern of text in the file.
        :param client_server: 'client' or 'server'
        :param text: pattern of text (str)
        :param path: full path include the name of file (str)
        :return: True or False
        """
        logging.info('Read from {} and search the text - {}'.format(path, text))
        result = self.machines[client_server]('grep {} {}'.format(text, path))
        return result

    def change_exports_file(self, share_name, host_client, mode):
        """
        The class method change file 'exports' with properties, write over there client IP and access rights.
        :param share_name: full path share name (str)
        :param host_client: host of client for NFS access (str)
        :param mode: 'ro' - read-only, 'rw' - read-write (str)
        :return: True - if host was added, or False - if not.
        """
        change_result = False
        logging.info('Trying change client\'s property to {}'.format(constants.EXPORTS_PATH))
        with open(constants.EXPORTS_PATH, 'w') as file_exports:
            file_exports.write('\n{}  {} ({},all_squash,sync)\n'.format(share_name, host_client, mode))
        with open(constants.EXPORTS_PATH, 'r') as file_exports:
            text_in_file = file_exports.readlines()
            for line in text_in_file:
                if host_client and share_name in line:
                    logging.info('Client\'s host is changed from /etc/exports')
                    change_result = True
                    break
        return change_result

    def check_sum(self, client_server, path):
        """
        The method counting of the check-sum of the file
        :param client_server: str 'client' or 'server'
        :param path: full path from the file
        :return: True False - result of command; sum_value - str include value of the check-sum
        """
        logging.info('Count check-sum of file in the share directory')
        result, sum_value = self.machines[client_server]('md5sum {}'.format(path))
        return result, sum_value
