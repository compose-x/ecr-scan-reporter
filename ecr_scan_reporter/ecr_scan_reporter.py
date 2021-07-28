#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille<john@compose-x.io>

from os import environ

DEFAULT_THRESHOLDS = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}


def import_thresholds():
    """
    Function to set thresholds from env vars or use from default
    :return:
    """
    thresholds = {
        "CRITICAL": int(environ.get("CRITICAL", DEFAULT_THRESHOLDS["CRITICAL"])),
        "HIGH": int(environ.get("HIGH", DEFAULT_THRESHOLDS["HIGH"])),
        "MEDIUM": int(environ.get("MEDIUM", DEFAULT_THRESHOLDS["MEDIUM"])),
        "LOW": int(environ.get("LOW", DEFAULT_THRESHOLDS["LOW"])),
    }
    return thresholds


def parse_scan_report(event, thresholds):
    """

    :param dict event:
    :param dict thresholds:
    :return:
    """
    scan_details = event["detail"]
    if "scan-status" not in scan_details.keys():
        print("NO SCAN STATUS GIVEN??", event)
        return
    elif "scan-status" in scan_details.keys() and scan_details["scan-status"] == "FAILED":
        print("Scan failed", event)
        return {"reason": "Failed to scan the image"}
    elif "scan-status" in scan_details.keys() and scan_details["scan-status"] == "COMPLETE":
        if "finding-severity-counts" not in scan_details.keys() or not scan_details["finding-severity-counts"]:
            return
        else:
            findings = scan_details["finding-severity-counts"]
            for level, threshold in thresholds.items():
                if level in findings.keys() and findings[level] >= threshold:
                    findings["reason"] = "Findings above defined thresholds"
                    return findings, thresholds, scan_details["image-digest"], scan_details["image-tags"]
