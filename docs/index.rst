=================
ECR Scan Reporter
=================


.. image:: https://img.shields.io/pypi/v/ecr_scan_reporter.svg
        :target: https://pypi.python.org/pypi/ecr_scan_reporter


------------------------------------------------------------------------------------
Serverless Application to monitor ECR Repositories and capture scan results
------------------------------------------------------------------------------------

Workflow
==========

.. image:: EcrScanReporterWorkflow.jpg

Full documentation https://ecr-scan-reporter.compose-x.io.


Installation
===============

From AWS Serverless Application Repository
---------------------------------------------

https://serverlessrepo.aws.amazon.com/applications/eu-west-1/518078317392/ecr-scan-reporter

From pip as a CLI
------------------

.. code-block:: console

    # Into a virtual env
    python -m venv venv
    source venv/bin/activate
    pip install ecr-scan-reporter

    # For local user only
    pip install ecr-scan-reporter --user

Usage
======

This package can be used as a CLI tool, but mainly was designed to be deployed in AWS.
See installation `From AWS Serverless Application Repository`_ for more information.

As CLI
-------

.. code-block:: console




Credits
========

This package was created with Cookiecutter_.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage

.. toctree::
   :maxdepth: 2
   :caption: Additional Info:

   modules
   contributing
   authors
   history

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
