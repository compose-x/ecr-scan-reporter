.. meta::
    :description: ECR Scan Reporter usage
    :keywords: AWS, ECR, Docker, vulnerabilities, scan, serverless

=====
Usage
=====

.. tip::

    This package can be used as a CLI tool, but mainly was designed to be deployed in AWS.
    See installation :ref:`sam_sar_install` for more information.


As AWS SAM Application
-----------------------

The SAM application you can install from `AWS SAR Page for ECR Scan Reporter`_ will deploy 3 Lambda functions
which will be triggered based on their usage. It will also be deploying a Lambda Layer which contains the
application source code of this repository so to make it simple to update all 3 functions together without making their
code too complex.

Scan images based on ECS Task Definitions
++++++++++++++++++++++++++++++++++++++++++++

If you have a lot of images and repositories, it might be more beneficial to scan only the images that are currently
in-use in AWS ECS. AWS ECS Task Definitions can be used to create services into AWS ECS Clusters, and contain the definition
of the containers to use for the service.

By defining **ECS_DISCOVERY_ROLES** (Parameter *ScanFromEcsIamRoles* in CloudFormation) the Lambda function will assume
role (same or cross-account, so long as it allows to describe ECS task definitions), retrieve the repository and images
to perform the scan for.

.. hint::

    This feature is (currently) only available currently via using AWS Lambda.

As CLI
-------

.. code-block:: console

    ecr_scan_reporter -h
    usage: ecr_scan_reporter [-h] [--profile PROFILE] [--region REGION] [--repos-regex REPOS_REGEX] [--duration-override DURATION_OVERRIDE] [--no-scanning] [_ ...]

    positional arguments:
      _

    optional arguments:
      -h, --help            show this help message and exit
      --profile PROFILE     AWS Profile name to use for API Calls
      --region REGION       AWS Region to scan ECR Repos for
      --repos-regex REPOS_REGEX
                            Regular expression to filter repositories names
      --duration-override DURATION_OVERRIDE
                            The time period expressed in m|w|d expressing the time delta to scan images from
      --no-scanning         Whether or not trigger a scan of the images identified


.. _AWS SAR Page for ECR Scan Reporter: https://serverlessrepo.aws.amazon.com/applications/eu-west-1/518078317392/ecr-scan-reporter
