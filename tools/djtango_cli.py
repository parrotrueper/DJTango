#!/usr/bin/env python3
# -*- coding:Utf-8 -*-

import argparse
import os
import sys
from pathlib import Path

from djtango.data import djDataConnection
from djtango.dirsong import dirSong


DEFAULT_HOME = os.environ.get('DJ_HOME_PATH', str(Path.home() / '.djtango'))


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog='djtango',
        description='DJ Tango CLI: manage tango music libraries without Qt.',
    )
    parser.add_argument('--home', default=DEFAULT_HOME, help='DJ home directory for the database')
    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('init-db', help='Create the DJ Tango database in the home directory.')

    scan_parser = subparsers.add_parser('scan', help='Scan a directory and insert supported audio files into the database.')
    scan_parser.add_argument('path', help='Path to scan for tango audio files')

    list_parser = subparsers.add_parser('list', help='List all songs in the database.')
    list_parser.add_argument('--limit', type=int, default=0, help='Limit the number of rows printed')

    missing_parser = subparsers.add_parser('check-new', help='List files on disk that are not yet in the database.')
    missing_parser.add_argument('path', help='Path to scan for new files')

    missing_db_parser = subparsers.add_parser('check-missing', help='List database entries whose files are missing on disk.')
    missing_db_parser.add_argument('path', help='Path to use as the song root for missing-file detection')

    return parser.parse_args(argv)


def init_db(args):
    data = djDataConnection(args.home)
    data.createDatabase()
    print(f'Created database at {data.path}')


def scan_path(args):
    data = djDataConnection(args.home)
    if not os.path.exists(data.path):
        data.createDatabase()

    scanner = dirSong(cpath=args.path, fill=False, djData=data)
    scanner.fillListOfFile()
    print(f'Scanned {args.path} and inserted {len(scanner.tangos)} songs.')


def list_songs(args):
    data = djDataConnection(args.home)
    tangos = data.getAllTangos()
    count = 0
    for tango in tangos:
        count += 1
        print(f'{tango.ID}\t{tango.path}\t{tango.title}\t{tango.artist}\t{tango.album}\t{tango.type}\t{tango.year}')
        if args.limit and count >= args.limit:
            break
    print(f'Found {len(tangos)} songs.')


def check_new(args):
    data = djDataConnection(args.home)
    tangos = data.getAllTangos()
    scanner = dirSong(cpath=args.path, fill=False, djData=data)
    scanner.loadTangos(tangos)
    new_files = scanner.checkNewFiles()
    if not new_files:
        print('No new files detected.')
        return
    print('New files not in database:')
    for file_path in new_files:
        print(file_path)


def check_missing(args):
    data = djDataConnection(args.home)
    tangos = data.getAllTangos()
    scanner = dirSong(cpath=args.path, fill=False, djData=data)
    scanner.loadTangos(tangos)
    missing = scanner.getMissedFiles()
    if not missing:
        print('No missing files detected.')
        return
    print('Missing database entries:')
    for file_path in missing:
        print(file_path)


def main(argv=None):
    args = parse_args(argv)
    if args.command == 'init-db':
        init_db(args)
    elif args.command == 'scan':
        scan_path(args)
    elif args.command == 'list':
        list_songs(args)
    elif args.command == 'check-new':
        check_new(args)
    elif args.command == 'check-missing':
        check_missing(args)
    else:
        raise SystemExit('Unknown command: ' + str(args.command))


if __name__ == '__main__':
    raise SystemExit(main())
