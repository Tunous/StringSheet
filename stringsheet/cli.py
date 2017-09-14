import argparse

import stringsheet.main as ss
from . import __version__


def create(args):
    ss.create(args.project_name, args.source_dir, args.multi_sheet)


def upload(args):
    ss.upload(args.spreadsheet_id, args.source_dir)


def download(args):
    ss.download(args.spreadsheet_id, args.target_dir)


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description='Manage Android translations using Google Spreadsheets',
        prog='stringsheet')

    arg_parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s ' + __version__)

    subparsers = arg_parser.add_subparsers(dest='operation')
    subparsers.required = True

    parser_create = subparsers.add_parser(
        'create',
        help='Create new Google Spreadsheet for managing Android strings')
    parser_create.add_argument(
        'project_name',
        help='The name of the project')
    parser_create.add_argument(
        'source_dir',
        help='A path to resources directory of Android project')
    parser_create.add_argument(
        '-m', '--multi-sheet',
        action='store_true',
        help='Upload each language to a separate sheet (in the same file)')
    parser_create.set_defaults(func=create)

    parser_upload = subparsers.add_parser(
        'upload',
        help='Upload Android strings to Google Spreadsheet')
    parser_upload.add_argument(
        'spreadsheet_id',
        help='Id of the spreadsheet to upload to')
    parser_upload.add_argument(
        'source_dir',
        help='A path to resources directory of Android project')
    parser_upload.set_defaults(func=upload)

    parser_download = subparsers.add_parser(
        'download',
        help='Download Google Spreadsheet as strings files')
    parser_download.add_argument(
        'spreadsheet_id',
        help='Id of the spreadsheet to download')
    parser_download.add_argument(
        'target_dir',
        help='A path to directory where to save downloaded strings')
    parser_download.set_defaults(func=download)

    return arg_parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
