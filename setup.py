#!/usr/bin/env python

import os
import re

from setuptools import find_packages, setup

DIR_HERE = os.path.abspath(os.path.dirname(__file__))
# REMOVE UNSUPPORTED RST syntax
REF_REGX = re.compile(r"(\:ref\:)")

try:
    with open(f"{DIR_HERE}/README.rst", encoding="utf-8") as readme_file:
        readme = readme_file.read()
        readme = REF_REGX.sub("", readme)
except FileNotFoundError:
    readme = "ECR Scan Reporter"

try:
    with open(f"{DIR_HERE}/HISTORY.rst", encoding="utf-8") as history_file:
        history = history_file.read()
except FileNotFoundError:
    history = "Latest packaged version."

requirements = []
with open(f"{DIR_HERE}/requirements.txt", "r") as req_fd:
    for line in req_fd:
        requirements.append(line.strip())

test_requirements = []
try:
    with open(f"{DIR_HERE}/requirements_dev.txt", "r") as req_fd:
        for line in req_fd:
            test_requirements.append(line.strip())
except FileNotFoundError:
    print("Failed to load dev requirements. Skipping")

setup_requirements = []

setup(
    author="John Preston",
    author_email="john@compose-x.io",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Application to monitor ECR Repositories and capture scan results",
    entry_points={
        "console_scripts": [
            "ecr_scan_reporter=ecr_scan_reporter.cli:main",
        ],
    },
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="ecr_scan_reporter aws ecr security vulnerabilities scan lambda severless",
    name="ecr_scan_reporter",
    packages=find_packages(include=["ecr_scan_reporter", "ecr_scan_reporter.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/compose-x/ecr_scan_reporter",
    version="0.1.0",
    zip_safe=False,
)
