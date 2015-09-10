#!/usr/bin/python
from ftplib import FTP
from datetime import datetime, timedelta
import getopt
import sys
import time

# Delete files older than maxage on a FTP server.

VERSION = 0.1

files_to_delete = []
now = datetime.now()
t = timedelta(days=1)
yesterday = now - t

def usage():
    print 'mason: missing flags'
    print "Try 'mason --help' for more information."

def help():
    print 'Usage: mason [OPTION]...'
    print 'Delete files older than maxage on a FTP server.'
    print ''
    print '  -H, --host\t\tFTP server to connect to'
    print '  -U, --user\t\tusername to authenticate with'
    print '  -P, --password\tpassword to authenticate with'
    print '  -M, --maxage\t\tmaximum age of backup files (in days)'
    print '  -v, --verbose\t\texplain what is being done'
    print '      --help\t\tdisplay this help and exit'
    print '      --version\t\toutput version information and exit'

def parse_list(file_str):
    file = file_str.split(';')
    filename = file[-1].strip()

    if filename != '.' and filename != '..':
        file_datetime = file[0].split('=')[1]
        datetime_obj = datetime.strptime(file_datetime, "%Y%m%d%H%M%S")

        if datetime_obj < yesterday:
            files_to_delete.append(filename)

def main(argv):
    host = ''
    user = ''
    password = ''
    maxage = 1
    _verbose = False
    _dry_run = False

    try:
        opts, args = getopt.getopt(argv, 'H:U:P:M:v', ['host=', 'user=', 'password=', 'maxage=', 'dry-run', 'verbose', 'help', 'version'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if len(opts) == 0:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '--help':
            help()
            sys.exit()
        elif opt in ('-H', '--host'):
            host = arg
        elif opt in ('-U', '--user'):
            user = arg
        elif opt in ('-P', '--password'):
            password = arg
        elif opt in ('-M', '--maxage'):
            maxage = int(arg)
        elif opt == '--dry-run':
            _dry_run = True
        elif opt in ('-v', '--verbose'):
            _verbose = True
        elif opt == '--version':
            print 'mason %s' % VERSION
            print 'Copyright (C) 2013 Pall Magnusson.'
            print 'License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.'
            print 'This is free software: you are free to change and redistribute it.'
            print 'There is NO WARRANTY, to the extent permitted by law.'
            sys.exit()

    t = timedelta(days=maxage)
    yesterday = now - t

    if host and user and password:
        if _verbose:
            print 'Connecting to %s...' % host
        ftp = FTP(host, user, password)

        if _verbose:
            print 'Fetching expired files...'
        ftp.retrlines('MLSD', parse_list)
        
        if _verbose and len(files_to_delete) == 0:
            print 'No expired files found.'

        for file in files_to_delete:
            if _verbose:
                print 'Deleting %s...' % file
            if not _dry_run:
                result = ftp.delete(file)
    else:
        help()
        sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])

