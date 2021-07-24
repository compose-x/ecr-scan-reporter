#!/usr/bin/env python


from os import path

import placebo
import pytest
from boto3 import session

HERE = path.abspath(path.dirname(__file__))

from ecr_scan_reporter.ecr_scan_reporter import import_thresholds, parse_scan_report


@pytest.fixture()
def with_findings():
    return {
        "version": "0",
        "id": "85fc3613-e913-7fc4-a80c-a3753e4aa9ae",
        "detail-type": "ECR Image Scan",
        "source": "aws.ecr",
        "account": "000000000000",
        "time": "2019-10-29T02:36:48Z",
        "region": "us-east-1",
        "resources": [
            "arn:aws:ecr:us-east-1:000000000000:repository/my-repository-name"
        ],
        "detail": {
            "scan-status": "COMPLETE",
            "repository-name": "my-repository-name",
            "finding-severity-counts": {"CRITICAL": 10, "MEDIUM": 9},
            "image-digest": "sha256:7f5b2640fe6fb4f46592dfd3410c4a79dac4f89e4782432e0378abcd1234",
            "image-tags": [],
        },
    }


@pytest.fixture()
def with_no_findings():
    return {
        "version": "0",
        "id": "85fc3613-e913-7fc4-a80c-a3753e4aa9ae",
        "detail-type": "ECR Image Scan",
        "source": "aws.ecr",
        "account": "000000000000",
        "time": "2019-10-29T02:36:48Z",
        "region": "us-east-1",
        "resources": [
            "arn:aws:ecr:us-east-1:000000000000:repository/my-repository-name"
        ],
        "detail": {
            "scan-status": "COMPLETE",
            "repository-name": "my-repository-name",
            "image-digest": "sha256:7f5b2640fe6fb4f46592dfd3410c4a79dac4f89e4782432e0378abcd1234",
            "image-tags": [],
        },
    }


@pytest.fixture()
def with_failed_scan():
    return {
        "version": "0",
        "id": "85fc3613-e913-7fc4-a80c-a3753e4aa9ae",
        "detail-type": "ECR Image Scan",
        "source": "aws.ecr",
        "account": "000000000000",
        "time": "2019-10-29T02:36:48Z",
        "region": "us-east-1",
        "resources": [
            "arn:aws:ecr:us-east-1:000000000000:repository/my-repository-name"
        ],
        "detail": {
            "scan-status": "FAILED",
            "repository-name": "my-repository-name",
            "image-digest": "sha256:7f5b2640fe6fb4f46592dfd3410c4a79dac4f89e4782432e0378abcd1234",
            "image-tags": [],
        },
    }


def test_with_findings(with_findings):
    """
    Test detection with findings
    :return:
    """
    thresholds = import_thresholds()
    findings = parse_scan_report(with_findings, thresholds)
    print("FINDINGS", findings)


def test_with_no_findings(with_no_findings):
    """
    Test detection with findings
    :return:
    """
    thresholds = import_thresholds()
    findings = parse_scan_report(with_no_findings, thresholds)
    print("FINDINGS", findings)


def test_with_failed(with_failed_scan):
    """
    Test detection with findings
    :return:
    """
    thresholds = import_thresholds()
    findings = parse_scan_report(with_failed_scan, thresholds)
    print("FINDINGS", findings)
