import logging
import os
import sys

import constants


def test_case_004(environment):
    """
    A test-case about access client to write file in read-write share directory on server.
    Include two steps:
     - change a property in share directory on server for client.
     - try to write a file in the mounted directory on client used SSH session.

    :param environment: fixture by py.test
    :return: result of the test Success or Crash which logging in log-file and display to screen
    """

    result_of_steps = []
    file_name = 'Test_4'

    environment.mount_nfs_share(constants.HOST_SERVER, constants.NFS_SHARE_NAME, constants.NFS_SHARE_NAME)
    logging.info('{} started...'.format(file_name))
    logging.info('STEP #1 Change a property in share directory on server for client.')
    result_1 = environment.change_exports_file(constants.NFS_SHARE_NAME, constants.HOST_CLIENT, 'rw')
    result_of_steps.append(result_1)
    logging.info('STEP #2 - Try to write a file in read-write share directory from the client.')
    result_2 = environment.make_file('client', constants.NFS_SHARE_NAME)
    result_of_steps.append(result_2)
    environment.positive_test_result(result_of_steps, file_name)

    environment.umount_nfs_share(constants.NFS_SHARE_NAME)
