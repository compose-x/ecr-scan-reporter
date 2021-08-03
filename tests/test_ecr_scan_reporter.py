#!/usr/bin/env python

"""Tests for `ecr_scan_reporter` package."""


from os import path

import placebo
from boto3 import session

HERE = path.abspath(path.dirname(__file__))

from ecr_scan_reporter.images_scanner import (
    define_images_to_scan,
    list_all_images,
    trigger_images_scan,
    update_all_images_timestamp,
)
from ecr_scan_reporter.repos_scanner import filter_repos_from_regexp, list_ecr_repos


def test_list_ecr_repos():
    ecr_session = session.Session(profile_name="ews")
    pill = placebo.attach(ecr_session, data_path=f"{HERE}/placebos/ecr/")
    # pill.record()
    pill.playback()
    repos = list_ecr_repos(ecr_session=ecr_session)


def test_default_fitler_repos():
    ecr_session = session.Session(profile_name="ews")
    pill = placebo.attach(ecr_session, data_path=f"{HERE}/placebos/ecr/")
    # pill.record()
    pill.playback()
    repos = list_ecr_repos(ecr_session=ecr_session)
    filtered_repos = filter_repos_from_regexp(repos)


def test_fitlered_repos():
    ecr_session = session.Session(profile_name="ews")
    pill = placebo.attach(ecr_session, data_path=f"{HERE}/placebos/ecr/")
    # pill.record()
    pill.playback()
    repos = list_ecr_repos(ecr_session=ecr_session)
    filtered_repos = filter_repos_from_regexp(repos, repos_names_filter=r"^python.*$")
    expected = ["python"]
    assert all(name in expected for name in filtered_repos)


def test_images_timestamps_repos():
    ecr_session = session.Session(profile_name="ews")
    pill = placebo.attach(ecr_session, data_path=f"{HERE}/placebos/ecr/")
    # pill.record()
    pill.playback()
    repos = list_ecr_repos(ecr_session=ecr_session)
    filtered_repos = filter_repos_from_regexp(repos, repos_names_filter=r"^python.*$")
    expected = ["python"]
    assert all(name in expected for name in filtered_repos)
    images = list_all_images("python", ecr_session=ecr_session)
    update_all_images_timestamp("python", images, ecr_session=ecr_session)
    print(images)
    scans = define_images_to_scan(images, duration_override="1w")
    trigger_images_scan("python", scans, ecr_session=ecr_session)
