import logging
import constants

import os
import sys

from commands import Commands
from fixture.ssh_session import SSHSession

logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO,
                    filename=constants.NAME_LOG_FILE, filemode='w+')


class PrepareError(Exception):
    """
    The custom Exceptions for preparation before test-suit
    """

    def __str__(self):
        return 'PrepareError: Preparing was NOT completed, you can NOT run tests! Read logs-file,' \
               ' correct mistake and try again.'


class CleaningError(Exception):
    """
    The custom Exceptions for cleaning after test-suit
    """

    def __str__(self):
        return 'Warning: the cleaning was NOT completed, some of product from your tests maybe stay! Check carefully ' \
               'and clean manually.'


def prepare_decor(fn):
    """
    A decorator for function links setup methods with Exception of prepare.
    :param fn:
    :return: fn(*args) or raise PrepareError
    """

    def wrapper(*args):
        try:
            fn(*args)
        except PrepareError:
            logging.exception('Exception:')
            print('{}\nFile with logs you can reed in {}'.format(PrepareError,
                                                                 os.path.abspath(constants.NAME_LOG_FILE)))
            sys.exit()

    return wrapper


def cleaning_decor(fn):
    """
        A decorator for function links teardown methods with Exception of cleaning.
        :param fn:
        :return: fn(*args) or raise CleaningError
        """

    def wrapper(*args):
        try:
            fn(*args)
        except CleaningError:
            logging.exception('Exception:')
            print('{}\nFile with logs you can reed in {}'.format(CleaningError,
                                                                 os.path.abspath(constants.NAME_LOG_FILE)))
            sys.exit()

    return wrapper


class StepAndMethod(Commands):
    """
    the class have methods for steps, setup and teardown of tests.
    """

    def __init__(self):
        super(StepAndMethod, self).__init__()
        self.session = SSHSession()
        self.setup()

    @prepare_decor
    def install_nfs(self, client_or_server):
        """
        Thr method is used for install nfs-utils such on the server us on the client, depends on the parameter.
        Firstly, the method check to NFS-package was not installed and if not then startup installation.
        :param client_or_server: have a value 'server' or 'client'
        :return:
        """
        check = self.check_nfs(client_or_server)
        if not check:
            self.cmd_install_nfs(client_or_server)
        else:
            logging.info('nfs-utils has just been installed on {}'.format(client_or_server))

    @prepare_decor
    def start_processes(self, client_or_server):
        """
        The method of class starts the necessary services of NFS on the machine (server or client)
        in depends of value parameter.
        :param client_or_server: have a value 'server' or 'client'
        :return:
        """
        self.service_on(client_or_server)

    @prepare_decor
    def make_share_dir(self, client_or_server):
        """
        The method of class make a share directory on the machine (server or client)
        in depends of value parameter. After that it tries to make file over there and delete it.
        :param client_or_server: have a value 'server' or 'client'
        :return:
        """
        self.make_dir(client_or_server, constants.NFS_SHARE_NAME)
        self.make_file(client_or_server, '{}/Test'.format(constants.NFS_SHARE_NAME))
        self.remove(client_or_server, '{}/Test'.format(constants.NFS_SHARE_NAME))

    @prepare_decor
    def exports_file(self):
        """
        The class method change file 'exports' with properties, write over there client IP and access rights.
        :return: True - if host was added, or False - if not.
        """
        logging.info('Trying add client\'s property to {}'.format(constants.EXPORTS_PATH))
        with open(constants.EXPORTS_PATH, 'w') as file_exports:
            file_exports.write('\n{}  {} (ro,all_squash,sync)\n'.format(constants.NFS_SHARE_NAME,
                                                                        constants.HOST_CLIENT))
        with open(constants.EXPORTS_PATH, 'r') as file_exports:
            text_in_file = file_exports.readlines()
            for line in text_in_file:
                if constants.HOST_CLIENT and constants.NFS_SHARE_NAME in line:
                    logging.info('Client\'s host is added to /etc/exports')
                    break

    @cleaning_decor
    def cleaning(self):
        """
        The class method is used for cleaning after tests.
        :return:
        """
        logging.info('Clean the server after everyone Tests')
        self.clean_export_file()
        self.restart_nfs_server()
        for machine in constants.TYPE_OF_MACHINES:
            self.remove(machine, constants.NFS_SHARE_NAME, 'directory')
        self.session.ssh_close()
        logging.info('\nTests_success - {},\nTests_not_success - {}'.format(constants.TEST_SUCCESS,
                                                                          constants.TEST_NOT_SUCCESS))
        print('''\nTests_success - {},\nTests_not_success - {}
        Logs you can reed in {}'''.format(constants.TEST_SUCCESS, constants.TEST_NOT_SUCCESS,
                                          os.path.abspath(constants.NAME_LOG_FILE)))

    def setup(self):
        """
        The class method starts preparation for tests, install and setting nfs for server and client
        :return:
        """
        logging.info('Preparation of system is started')
        self.session.ssh_connect()
        for machine in constants.TYPE_OF_MACHINES:
            self.install_nfs(machine)
            self.start_processes(machine)
            self.make_share_dir(machine)
        self.change_firewall_ports()
        self.exports_file()
        self.restart_nfs_server()
        logging.info('Preparation of server and client is completed!')

    def create_file(self, client_or_server, file_name):
        """
        The class method creates file for test, consist the checking of result.
        :param client_or_server: have a value 'server' or 'client'
        :param file_name: str
        :return: True or False
        """
        with open('{}/{}'.format(constants.NFS_SHARE_NAME, file_name), 'w') as new_file:
            new_file.write('{} is running!'.format(file_name))
        result = self.search_text_in_file(client_or_server, file_name, '{}/{}'.format(constants.NFS_SHARE_NAME,
                                                                                      file_name))
        return result

    def positive_test_result(self, result_of_steps, test):
        """
        The method analysing result ich of the test's steps and count success tests (if these test is positive)
        :param result_of_steps: list of bool value
        :param test: test name (test number) which is doing now
        :return: True if test was success or False - if not
        """
        step = 0
        positive_test = False
        for result in result_of_steps:
            step += 1
            if result:
                logging.info('STEP {} - success'.format(step))
            else:
                logging.info('Step {} - Error!\n {} crashed!'.format(step, test))
                constants.TEST_NOT_SUCCESS += 1
                break
            positive_test = True
        if positive_test:
            logging.info('{} finish success.\n'.format(test))
            constants.TEST_SUCCESS += 1
        return positive_test

