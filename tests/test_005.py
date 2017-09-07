import logging
import os
import sys

import constants


def test_case_005(environment):
    """
    A test-case about comparison check-sum of file on share folder to count on server and on client.
    Include four steps:
     - write file in read-only share directory on server
     - count check-sum of the file on server side
     - count check-sum of the file on client side
     - comparison of the results

    :param environment: fixture by py.test
    :return: result of the test Success or Crash which logging in log-file and display to screen
    """

    result_of_steps = []
    file_name = 'Test_5'

    environment.mount_nfs_share(constants.HOST_SERVER, constants.NFS_SHARE_NAME, constants.NFS_SHARE_NAME)
    logging.info('{} started...'.format(file_name))
    logging.info('STEP #1 Create file in share directory of server')
    result_1 = environment.create_file('server', file_name)
    result_of_steps.append(result_1)
    logging.info('STEP #2 - Count check-sum of the file on server side')
    result_2, out_2 = environment.check_sum('server', '{}/{}'.format(constants.NFS_SHARE_NAME, file_name))
    logging.info('STEP #3 - Count check-sum of the file on client side')
    result_3, out_3 = environment.check_sum('client', '{}/{}'.format(constants.NFS_SHARE_NAME, file_name))
    logging.info('STEP #4 - Comparison the both value of check-sum of the file')
    if out_2 == out_3:
        result_of_steps.append('True')
    environment.positive_test_result(result_of_steps, file_name)

    environment.umount_nfs_share(constants.NFS_SHARE_NAME)
