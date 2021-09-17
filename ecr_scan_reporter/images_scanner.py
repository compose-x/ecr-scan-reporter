#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille<john@compose-x.io>

"""
Module to define images to scan.
"""


import re
import warnings
from datetime import datetime as dt
from os import environ
from time import sleep

from boto3 import session
from compose_x_common.compose_x_common import keyisset
from dateutil.relativedelta import relativedelta
from pytz import utc

from ecr_scan_reporter.common import chunked_iterable

DURATIONS_RE = re.compile(r"(?P<months>\dm)?(?P<weeks>\dw)?(?P<days>\dd)?(?P<hours>\dh)?")
DEFAULT_DURATION = "7d"
NOW = dt.utcnow()


def get_duration(duration_exp=None, env_key=None):
    """
    Function to define the time delta

    :param str duration_exp:
    :param str env_key:
    :return:
    """
    if not duration_exp:
        duration_exp = DEFAULT_DURATION
    if isinstance(env_key, str):
        duration_exp = environ.get(env_key, duration_exp)
    else:
        duration_exp = environ.get("ECR_IMAGES_DURATION_DELTA", duration_exp)
    if not DURATIONS_RE.match(duration_exp):
        warnings.warn(
            f"The provided duration, {duration_exp}, does not match expected regexp "
            f"{DURATIONS_RE.pattern}. Using default of 7days"
        )
    hours = (
        int(re.sub(r"[^\d]", "", DURATIONS_RE.match(duration_exp).group("hours")))
        if DURATIONS_RE.match(duration_exp).group("hours")
        else 0
    )
    days = (
        int(re.sub(r"[^\d]", "", DURATIONS_RE.match(duration_exp).group("days")))
        if DURATIONS_RE.match(duration_exp).group("days")
        else 0
    )
    weeks = (
        int(re.sub(r"[^\d]", "", DURATIONS_RE.match(duration_exp).group("weeks")))
        if DURATIONS_RE.match(duration_exp).group("weeks")
        else 0
    )
    months = (
        int(re.sub(r"[^\d]", "", DURATIONS_RE.match(duration_exp).group("months")))
        if DURATIONS_RE.match(duration_exp).group("months")
        else 0
    )
    up_to = NOW - relativedelta(months=months, weeks=weeks, days=days, hours=hours)
    return up_to


def update_image_info(image, detail):
    """
    Function to update the image definition to UHD - Utterly Helpful Definition

    :param dict image:
    :param dict detail:
    :return:
    """
    if not keyisset("imageDigest", image) and not keyisset("imageTag", image):
        print(f"No imageDigest or imageTag provided for {image}")
        return
    if keyisset("imageDigest", image) and image["imageDigest"] == detail["imageDigest"]:
        image.update({"imagePushedAt": detail["imagePushedAt"]})
        if keyisset("imageScanFindingsSummary", detail):
            scan_details = detail["imageScanFindingsSummary"]
            if keyisset("vulnerabilitySourceUpdatedAt", scan_details) and scan_details["vulnerabilitySourceUpdatedAt"]:
                image.update({"vulnerabilitySourceUpdatedAt": scan_details["vulnerabilitySourceUpdatedAt"]})


def update_all_images_timestamp(repo_name, source_images, batch=False, ecr_session=None):
    """
    Function to describe images to retrieve additional information (imagePushedAt) to then be able to evaluate
    whether we want to scan that image

    :param str repo_name:
    :param list source_images:
    :param bool batch:
    :param boto3.session.Session ecr_session:
    """
    if not ecr_session:
        ecr_session = session.Session()
    client = ecr_session.client("ecr")
    if batch:
        chunk_size = 21
    else:
        chunk_size = 1
    chunks = chunked_iterable(source_images, size=chunk_size)
    for image in chunks:
        try:
            res = client.describe_images(repositoryName=repo_name, imageIds=list(image), filter={"tagStatus": "ANY"})
            for detail in res["imageDetails"]:
                for chunk in image:
                    update_image_info(chunk, detail)
        except client.exceptions.ImageNotFoundException:
            print(f"Could not find image {image} in repo {repo_name}.")
            warnings.warn(
                "If you are using ECS discovery, this can lead into critical issues and new services"
                " deployments failures!"
            )


def list_all_images(repo_name, images=None, next_token=None, ecr_session=None):
    """
    Retrieves all the images of a given repository

    :param str repo_name:
    :param images:
    :param next_token:
    :param boto3.session.Session ecr_session:
    :return:
    """
    if not ecr_session:
        ecr_session = session.Session()
    client = ecr_session.client("ecr")
    if images is None:
        images = []
    if not next_token:
        res = client.list_images(maxResults=42, repositoryName=repo_name, filter={"tagStatus": "ANY"})
    else:
        res = client.list_images(
            maxResults=42,
            repositoryName=repo_name,
            nextToken=next_token,
            filter={"tagStatus": "ANY"},
        )
    images += res["imageIds"]
    if "nextToken" in res.keys() and res["nextToken"]:
        return list_all_images(
            repo_name,
            images=images,
            next_token=res["nextToken"],
            ecr_session=ecr_session,
        )
    return images


def define_images_to_scan(images, duration_override=None, duration_env_key=None):
    """
    Return the list of images that need to get a scan started

    :param list images:
    :param str duration_override:
    :param str duration_env_key:
    :return: List of images past the timestamp
    :rtype: list
    """
    checkpoint = None
    delta = utc.localize(get_duration(duration_override, duration_env_key))
    images_to_scan = []
    scan_source = "imagePushedAt"
    for image in images:
        if keyisset("vulnerabilitySourceUpdatedAt", image) and isinstance(image["vulnerabilitySourceUpdatedAt"], dt):
            scan_source = "vulnerabilitySourceUpdatedAt"
            checkpoint = image[scan_source]

        if not checkpoint and keyisset("imagePushedAt", image) and isinstance(image["imagePushedAt"], dt):
            checkpoint = image[scan_source]
        if checkpoint and isinstance(checkpoint, dt) and checkpoint < delta:
            # print(f"Adding image due to {scan_source}", image[scan_source])
            images_to_scan.append(image)
    return images_to_scan


def trigger_images_scan(repo_name, images_to_scan, ecr_session=None):
    """
    Function to trigger the image scanning

    :param str repo_name: Name of the repository in your account registry
    :param list images_to_scan: List of images to get a scan started for
    :param boto3.session.Session ecr_session: override session
    :return:
    """
    if ecr_session is None:
        ecr_session = session.Session()
    client = ecr_session.client("ecr")
    chunks = chunked_iterable(images_to_scan, size=4)
    for images in chunks:
        for image in images:
            if not keyisset("imageDigest", image) and not keyisset("imageTag", image):
                warnings.warn(f"Neither imageDigest nor imageTag provided in {repo_name} - {image}.")
                continue
            tries = 3
            attempts_max = 4
            while tries:
                try:
                    image_id = {}
                    if keyisset("imageDigest", image):
                        image_id["imageDigest"] = image["imageDigest"]
                    if keyisset("imageTag", image):
                        image_id["imageTag"] = image["imageTag"]
                    client.start_image_scan(
                        repositoryName=repo_name,
                        imageId=image_id,
                    )
                    break
                except client.exceptions.LimitExceededException:
                    tries -= 1
                    sleep((attempts_max - tries) * 10)
                    print(
                        f"API Limit Exceeded. Attempt {(attempts_max - tries)} in another "
                        f"{((attempts_max - tries) * 10)} seconds"
                    )
                except client.exceptions.ImageNotFoundException:
                    print("No image found with provided tag or digest.", image)
                    tries = 0
                except client.exceptions.UnsupportedImageTypeException:
                    print("The image does not support scanning.")
                    tries = 0


def scan_repo_images(repo, repo_images=None, duration_override=None, no_scan_images=False, ecr_session=None):
    if ecr_session is None:
        ecr_session = session.Session()
    batch = False
    if not repo_images:
        repo_images = list_all_images(repo, ecr_session=ecr_session)
        batch = True
    update_all_images_timestamp(repo, repo_images, batch=batch, ecr_session=ecr_session)
    images_to_scan = define_images_to_scan(repo_images, duration_override)
    if images_to_scan:
        print(f"{repo} - There are {len(images_to_scan)} images that require scanning.")
        if no_scan_images:
            print("Skipping scan due to --no-scanning")
            return
    else:
        print(f"No images need scanning for {repo}")
        return
    trigger_images_scan(repo, images_to_scan, ecr_session=ecr_session)
