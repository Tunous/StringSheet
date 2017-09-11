import argparse

import stringsheet.main as ss


def upload(args):
    ss.upload(args.spreadsheet_id, args.source_dir, args.project_title)


def download(args):
    ss.download(args.spreadsheet_id, args.target_dir)


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description='Manage Android translations using Google Spreadsheets',
        prog='stringsheet')

    arg_parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 0.1.0')

    subparsers = arg_parser.add_subparsers(dest='operation')
    subparsers.required = True

    parser_upload = subparsers.add_parser(
        'upload',
        help='Upload Android strings to Google Spreadsheet')
    parser_upload.add_argument(
        'source_dir',
        help='A path to resources directory of Android project')
    group = parser_upload.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '-i', '--spreadsheet-id',
        help='Id of the spreadsheet for use')
    group.add_argument(
        '-p', '--project-title',
        help="The title of project for new spreadsheet")
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
