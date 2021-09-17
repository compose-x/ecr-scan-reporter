#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille<john@compose-x.io>

import re

from boto3.session import Session
from compose_x_common.aws import get_assume_role_session
from compose_x_common.aws.ecr import PRIVATE_ECR_URI_RE
from compose_x_common.compose_x_common import keyisset


def list_all_task_definitions(definitions=None, next_token=None, ecs_session=None):
    """
    Simple recursive function to list all the task definitions into an account+region.

    :param list definitions:
    :param str next_token:
    :param boto3.session.Session ecs_session:
    :return: list of active task definitions
    :rtype: list
    """
    if ecs_session is None:
        ecs_session = Session()
    client = ecs_session.client("ecs")
    if definitions is None:
        definitions = []
    if next_token:
        defs_r = client.list_task_definitions(nextToken=next_token, status='ACTIVE')
    else:
        defs_r = client.list_task_definitions(status='ACTIVE')
    definitions += defs_r["taskDefinitionArns"]
    if keyisset("nextToken", defs_r):
        return list_all_task_definitions(definitions, defs_r["nextToken"], ecs_session)
    return definitions


def list_container_definitions_images(task_definition, ecs_session=None):
    """
    Simple function to list the images of a given task definition

    :param str task_definition:
    :param boto3.session.Session ecs_session:
    :return: list of images
    :rtype: list
    """
    if ecs_session is None:
        ecs_session = Session()
    client = ecs_session.client("ecs")
    task_def = client.describe_task_definition(
        taskDefinition=task_definition,
        include=[
            'TAGS',
        ],
    )["taskDefinition"]
    images = [container["image"] for container in task_def["containerDefinitions"]]
    return images


def transform_image_description(images):
    """
    Function to update all images based on URL to get tag/digest etc.
    :param list[str] images:
    :return:
    """
    registries = {}
    for image in images:
        parts = PRIVATE_ECR_URI_RE.match(image)
        if not parts:
            print(f"Image {image} does not match Private ECR Images regexp", PRIVATE_ECR_URI_RE.pattern, "Skipping")
            continue
        registry = parts.group("account_id")
        tag = parts.group("tag")
        tag = re.sub(r"^:|^@", "", tag)
        repo_name = parts.group("repo_name")
        if registry not in registries.keys():
            registries[registry] = {}
        if repo_name not in registries[registry].keys():
            registries[registry][repo_name] = {"imageDigests": [], "imageTags": []}
        if tag.startswith("sha") and tag not in registries[registry][repo_name]["imageDigests"]:
            registries[registry][repo_name]["imageDigests"].append(tag)
        elif not tag.startswith("sha") and tag not in registries[registry][repo_name]["imageTags"]:
            registries[registry][repo_name]["imageTags"].append(tag)
    print(registries)
    return registries


def build_services_images_registries(roles=None, lambda_session=None):
    if lambda_session is None:
        lambda_session = Session()
    if roles and isinstance(roles, str):
        roles = roles.split(",")
    elif roles and not isinstance(roles, list):
        raise TypeError("roles must either be comma delimited list string or a list of IAM roles")
    images = []
    if not roles:
        task_definitions = list_all_task_definitions(ecs_session=lambda_session)
        for task_def in task_definitions:
            images += list_container_definitions_images(task_def, ecs_session=lambda_session)
    else:
        for role_arn in roles:
            ecs_session = get_assume_role_session(lambda_session, role_arn, session_name="ECRScanner")
            task_definitions = list_all_task_definitions(ecs_session=ecs_session)
            for task_def in task_definitions:
                images += list_container_definitions_images(task_def, ecs_session=ecs_session)
    registries = transform_image_description(images)
    return registries


def handle_ecs_discovery(roles=None, lambda_session=None):
    if lambda_session is None:
        lambda_session = Session()
    registries = build_services_images_registries(roles, lambda_session)
    account = lambda_session.client("sts").get_caller_identity()["Account"]
    jobs = []
    for registry_id, registry in registries.items():
        if registry_id != account:
            print(
                f"The registry {registry_id} is in a different account. Not performing image scan. Skipping images",
                registry.keys(),
            )
            continue
        for repo_name, images in registry.items():
            images_ids = []
            for digest in images["imageDigests"]:
                images_ids.append({"imageDigest": digest})
            for tag in images["imageTags"]:
                images_ids.append({"imageTag": tag})
            jobs.append({"repositoryName": repo_name, "images": images_ids, "registryId": registry_id})
    return jobs
