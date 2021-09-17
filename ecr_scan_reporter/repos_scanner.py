#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille<john@compose-x.io>

"""Main module."""

import re
import uuid
from json import dumps

from boto3 import session

from ecr_scan_reporter.common import chunked_iterable

"""
Module to trigger ECR Repositories scans
"""

DEFAULT_REGEXP = re.compile(r"^.*$")


def list_ecr_repos(repos=None, next_token=None, ecr_session=None):
    """
    Function to retrieve all the ECR repositories

    :param repos:
    :param next_token:
    :param boto3.session.Session ecr_session:
    :return:
    """
    if repos is None:
        repos = []
    if not ecr_session:
        ecr_session = session.Session()
    client = ecr_session.client("ecr")
    if not next_token:
        res = client.describe_repositories()
    else:
        res = client.describe_repositories(nextToken=next_token)
    repos += res["repositories"]
    if "nextToken" in res and res["nextToken"]:
        return list_ecr_repos(repos=repos, next_token=res["nextToken"], ecr_session=ecr_session)
    return repos


def filter_repos_from_regexp(repos_list, repos_names_filter=None):
    """
    Function to filter repositories based their name and a regular expression

    :param repos_list:
    :param repos_names_filter:
    :return:
    """
    filtered_repos = []
    if repos_names_filter and isinstance(repos_names_filter, str):
        repos_filter = re.compile(repos_names_filter)
    else:
        repos_filter = DEFAULT_REGEXP
    for repo in repos_list:
        if isinstance(repo, dict):
            if "repositoryName" not in repo.keys():
                raise KeyError("Missing repository name from ")
            repo_name = repo["repositoryName"]
        elif isinstance(repo, str):
            repo_name = repo
        else:
            raise TypeError("The repo list must be a list of dicts or str. Got", type(repo))
        if repos_filter.match(repo_name):
            filtered_repos.append(repo_name)
    return filtered_repos


def job_dispatcher(queue_url, repos, sqs_session=None):
    """
    Sends a new job in SQS to distribute the images listing and scan for a given repository

    :param str queue_url:
    :param list[dict] repos:
    :param boto3.session.Session sqs_session:
    :return:
    """
    if not sqs_session:
        sqs_session = session.Session()
    client = sqs_session.client("sqs")
    for repo in repos:
        print(f"Sending job for {repo['repositoryName']}")
        client.send_message(QueueUrl=queue_url, MessageBody=dumps(repo))
