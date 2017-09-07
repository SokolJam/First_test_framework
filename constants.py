import time


#every constants which are used in framework
HOST_SERVER = '192.168.100.9'
HOST_CLIENT = '192.168.100.10'
EXIT_SUCCESS = 0
STDERR_EMPTY = ''
NAME_LOG_FILE = 'log_file.log'
SERVICES = ['rpcbind', 'nfs-server', 'nfs-lock', 'nfs-idmap']
FIREWALL_PORTS = ['111', '54302', '20048', '2049', '46666', '42955', '875']
EXPORTS_PATH = '/etc/exports'
TYPE_OF_MACHINES = ['server', 'client']
NFS_SHARE_NAME = '/home/nfs_share_{}'.format(str(int(time.time())))
TEST_SUCCESS = 0
TEST_NOT_SUCCESS = 0