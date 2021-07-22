#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille<john@compose-x.io>

"""
Lambda function handler
"""

import warnings
from json import JSONDecodeError, dumps, loads
from os import environ

from boto3 import session

from ecr_scan_reporter.ecr_scan_reporter import import_thresholds, parse_scan_report
from ecr_scan_reporter.images_scanner import scan_repo_images
from ecr_scan_reporter.repos_scanner import (
    filter_repos_from_regexp,
    job_dispatcher,
    list_ecr_repos,
)


def findings_handler(event, context):
    """
    Entry point fo lambda function

    :param dict event:
    :param context:
    :return:
    """
    thresholds = import_thresholds()
    report = parse_scan_report(event, thresholds)
    if not report:
        return
    if not environ.get("ECR_SNS_REPORT_TOPIC_ARN", None):
        return
    l_session = session.Session()
    sns = l_session.client("sns")
    repository_name = event["detail"]["repository-name"]
    message_json = {
        "default": f"Vulnerabilities found above threshold for {repository_name}",
        "email": f"Vulnerabilities found above threshold for {repository_name}",
        "http": f"Vulnerabilities found above threshold for {repository_name}",
        "https": f"Vulnerabilities found above threshold for {repository_name}",
    }
    res = sns.publish(
        TopicArn=environ.get("ECR_SNS_REPORT_TOPIC_ARN", None),
        Message=dumps(message_json, ensure_ascii=True),
        Subject=f"ECR Image Scan Vulnerabilities - {repository_name}",
        MessageStructure="json",
    )


def scans_job_handler(event, context):
    """
    Entry point for lambda function that will list the repositories and if SQS is defined,
    will dispatch singular scanning jobs.

    :param dict event:
    :param dict context:
    :return:
    """
    lambda_session = session.Session()
    regexp_override = environ.get("REPOSITORIES_FILTER_REGEXP", None)
    if (
        "repositoriesFilterRegexp" in event.keys()
        and event["repositoriesFilterRegexp"]
        and isinstance(event["repositoriesFilterRegexp"], str)
    ):
        regexp_override = event["repositoriesFilterRegexp"]
    repos_list = list_ecr_repos(ecr_session=lambda_session)
    filtered_repos_list = filter_repos_from_regexp(
        repos_list, repos_names_filter=regexp_override
    )
    queue_url = environ.get("IMAGES_SCAN_JOBS_QUEUE_URL", None)
    if (
        "jobsQueueUrl" in event.keys()
        and event["jobsQueueUrl"]
        and isinstance(event["jobsQueueUrl"], str)
    ):
        queue_url = event["jobsQueueUrl"]
    if queue_url is None:
        warnings.warn(
            "No QueueURL was provided. Attempting to complete task locally. Might run out of time"
        )
    else:
        job_dispatcher(queue_url, filtered_repos_list, lambda_session)


def repo_images_scanning_handler(event, context):
    """
    Lambda handler triggered by SQS Jobs getting into the queue

    :param dict event:
    :param dict context:
    """
    lambda_session = session.Session()
    records = event["Records"]
    for message in records:
        message = message["body"]
        if isinstance(message, str):
            try:
                body = loads(message)
            except JSONDecodeError:
                print("Failed to process the payload")
                raise
        else:
            raise TypeError("The body is of type", type(message), "Expected", str)
        if "repositoryName" not in body.keys():
            raise KeyError("No repositoryName was provided")
        scan_repo_images(body["repositoryName"], ecr_session=lambda_session)
