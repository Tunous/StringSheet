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

    subparsers = arg_parser.add_subparsers(dest='operation')
    subparsers.required = True

    parser_upload = subparsers.add_parser('upload', help='Upload strings files to spreadsheet')
    parser_upload.add_argument('-i', '--spreadsheet-id', default='',
                               help='Id of the spreadsheet for use')
    parser_upload.add_argument('-s', '--source-dir', default='.',
                               help='A path to resources directory of Android project')
    parser_upload.add_argument('-p', '--project-title', help="The title of project")
    parser_upload.set_defaults(func=upload)

    parser_download = subparsers.add_parser('download', help='Download spreadsheet as strings files')
    parser_download.add_argument('-i', '--spreadsheet-id', required=True,
                                 help='Id of the spreadsheet for use')
    parser_download.add_argument('-t', '--target-dir', default='.',
                                 help='A path to directory where to save downloaded strings')
    parser_download.set_defaults(func=download)

    return arg_parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
