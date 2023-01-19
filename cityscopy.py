#!/usr/bin/python

import argparse
from cityscopy.Scanner.Scanner import Scanner
from cityscopy.Setup.Setup import Setup
import sys
import os


def main():

    parser = argparse.ArgumentParser(
        prog="cityscopy",
        description="CityScoPY: A Scanner for MIT CityScope",
        epilog="Thank you for using CityScope!",
    )

    parser.add_argument('--cityscopy', '-c',
                        default=None,
                        required=True,
                        const='all',
                        nargs='?',
                        choices=['scan', 'keystone', 'setup'],
                        help='list servers, storage, or both (default: %(default)s)')

    parser.add_argument('--table_name', '-t',
                        action='store',
                        required=True,
                        help='table\'s name')
    args = parser.parse_args()

    # get the table name and make it lower case
    args.table_name = args.table_name.lower()

    # run the right command based on the input argument
    if args.cityscopy == 'scan':
        scanner = Scanner(CITYSCOPE_PRJ_NAME=args.table_name)
        scanner.scan()

    elif args.cityscopy == 'setup':
        setup = Setup(CITYSCOPE_PRJ_NAME=args.table_name)
        setup.setup()

    else:
        parser.print_help()
        sys.exit(1)

    #! start local UDP comms
    # # cityscopy.udp_listener()


if __name__ == '__main__':
    os.system('clear')
    print(
        '''
        >>>>>> CityScoPY: A Scanner for MIT CityScope >>>>>>>>


                            |||||||||||
                            |||||||||||
                                    |||
                                    |||
                                    |||
                            |||      ||||||||||||
                            |||      ||||||||||||
                            |||               |||
                            |||               |||
                            |||               |||
                            ||||||||||||      |||
                            ||||||||||||      |||



        Copyright (C) {{ 2018 - 2023 }}  {{ Ariel Noyman }}

        Ariel Noyman
        https://github.com/CityScope/
        http://arielnoyman.com
        https://github.com/RELNO

        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        '''
    )

    main()
