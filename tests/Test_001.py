import logging
import os
import sys

import constants


def test_case_001(environment):
    """
    A test-case about access client to read file in read-only share directory on server.
    Include two steps:
     - write file in read-only share directory on server
     - try to read this file in the mounted directory on client used SSH session.

    :param environment: fixture by py.test
    :return: result of the test Success or Crash which logging in log-file and display to screen
    """

    result_of_steps = []
    file_name = 'Test_1'

    environment.mount_nfs_share(constants.HOST_SERVER, constants.NFS_SHARE_NAME, constants.NFS_SHARE_NAME)
    logging.info('{} started...'.format(file_name))
    logging.info('STEP #1 Create file in read-only share directory of server')
    result_1 = environment.create_file('server', file_name)
    result_of_steps.append(result_1)
    logging.info('STEP #2 - Try to read the file in read-only share directory from the client.')
    result_2 = environment.search_text_in_file('client', file_name, '{}/{}'.format(constants.NFS_SHARE_NAME, file_name))
    result_of_steps.append(result_2)
    environment.positive_test_result(result_of_steps, file_name)

    environment.umount_nfs_share(constants.NFS_SHARE_NAME)
