#!/usr/bin/python3 -Es
import argparse
import getpass
import webdav.client as wc

parser = argparse.ArgumentParser()

parser.add_argument("-d", dest="destination", required=True,
                    help="path to store the downloaded files")
parser.add_argument("-s", dest="server", required=True,
                    help="Nextcloud server")
parser.add_argument("-r", dest="root", required=True,
                    help="root path for starting search")

args = parser.parse_args()
path = args.destination
server = args.server
root = args.root

try:
    username = input("User: ")
    password = getpass.getpass('Password: ')
except Exception as error:
    print('ERROR', error)

options = {
    'webdav_hostname': server,
    'webdav_login': username,
    'webdav_password': password,
    'webdav_root': "/remote.php/webdav"
}

webdav = wc.Client(options)

while True:
    # The pull will fail due to the server reporting the wrong size of
    # files. By looping the request and ignoring the exception we can
    # work past that. This is a very dirty hack, but at least this way
    # we can recover the files.
    try:
        webdav.pull(remote_directory=root, local_directory=path)
        break
    except:
        continue

print("successfully downloaded " + root)
