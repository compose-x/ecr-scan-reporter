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
