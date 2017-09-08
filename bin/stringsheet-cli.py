import argparse

import stringsheet.main as ss


def upload(args):
    ss.upload(args.spreadsheet_id)
    pass


def download(args):
    ss.download(args.spreadsheet_id)
    pass


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description='Manage Android translations using Google Spreadsheets',
        prog='stringsheet')

    subparsers = arg_parser.add_subparsers(dest='operation', metavar='<operation>')
    subparsers.required = True

    parser_upload = subparsers.add_parser('upload', help='Upload strings files to spreadsheet')
    parser_upload.add_argument('--spreadsheet_id', help='Id of the spreadsheet for use', default='')
    parser_upload.set_defaults(func=upload)

    parser_download = subparsers.add_parser('download', help='Download spreadsheet as strings files')
    parser_download.add_argument('--spreadsheet_id', help='Id of the spreadsheet for use', required=True)
    parser_download.set_defaults(func=download)

    return arg_parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
