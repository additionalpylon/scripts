#!/usr/bin/env python

'''
* Example script to create an EC2 and S3 connection with boto.
* Authenticates to AWS end points with either IAM Access Keys, IAM Role, or
 other method (credentials in boto.config, IAM Instance Profile, etc).
* Task description goes here.

Authentication arguments:
    Authenticate with IAM Keys:
        --aws_access_key_id                 # Keys to connect with
        --aws_secret_access_key             # Keys to connect with
    Authenticate with IAM Role:
        --aws_access_key_id                 # Keys to connect from
        --aws_secret_access_key             # Keys to connect from
        --aws_account_id                    # Used to form the role_arn
        --aws_role_name                     # Used to form the role_arn
        --aws_role_external_id              # Optional if set on the IAM Role
    Authenticate with other method:
        None                                # Pass no authentication arguments
'''


import os
import sys
import argparse
import boto
import boto.ec2
from boto.sts import STSConnection


def boto_conn(args):
    ec2_region = boto.ec2.get_region(region_name=args.aws_region)
    if (args.aws_access_key_id and
            args.aws_secret_access_key and
            args.aws_account_id and
            args.aws_role_name):
        sts_connection = STSConnection(
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key)
        AssumedRole = sts_connection.assume_role(
            role_arn='arn:aws:iam::%s:role/%s' % (args.aws_account_id,
                                                  args.aws_role_name),
            external_id=args.aws_role_external_id,
            role_session_name='AssumeRoleSession')
        ec2_conn = boto.connect_ec2(
            aws_access_key_id=AssumedRole.credentials.access_key,
            aws_secret_access_key=AssumedRole.credentials.secret_key,
            security_token=AssumedRole.credentials.session_token,
            region=ec2_region)
        s3_conn = boto.connect_s3(
            aws_access_key_id=AssumedRole.credentials.access_key,
            aws_secret_access_key=AssumedRole.credentials.secret_key,
            security_token=AssumedRole.credentials.session_token)

    elif args.aws_access_key_id and args.aws_secret_access_key:
        ec2_conn = boto.connect_ec2(
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
            region=ec2_region)
        s3_conn = boto.connect_s3(
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key)

    elif (not args.aws_access_key_id and not
            args.aws_secret_access_key and not
            args.aws_account_id and not
            args.aws_role_name and not
            args.aws_role_external_id):
        ec2_conn = boto.connect_ec2(region=ec2_region)
        s3_conn = boto.connect_s3()

    else:
        raise Exception('''Invalid authentication arguments.
                        Try --help for more information.''')
    return ec2_conn, s3_conn


def my_method(ec2_conn, s3_conn):
    print(ec2_conn, s3_conn)


def main(arguments):
    # Parse and validate arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--aws_access_key_id', dest='aws_access_key_id',
                        help=argparse.SUPPRESS, type=str)
    parser.add_argument('--aws_secret_access_key',
                        dest='aws_secret_access_key',
                        help=argparse.SUPPRESS, type=str)
    parser.add_argument('--aws_role_name', dest='aws_role_name',
                        help=argparse.SUPPRESS, type=str)
    parser.add_argument('--aws_role_external_id', dest='aws_role_external_id',
                        help=argparse.SUPPRESS, type=str)
    parser.add_argument('--aws_account_id', dest='aws_account_id',
                        help=argparse.SUPPRESS, type=int)
    parser.add_argument('--aws_region', dest='aws_region',
                        type=str, required=True)
    args = parser.parse_args(arguments)

    # Create connections with boto
    ec2_conn, s3_conn = boto_conn(args)

    # Perform desired task
    my_method(ec2_conn=ec2_conn, s3_conn=s3_conn)

    # Clean up
    pass


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
