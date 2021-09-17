"""Console script for ecr_scan_reporter."""

import argparse
import sys

from boto3 import session

from ecr_scan_reporter.images_scanner import scan_repo_images
from ecr_scan_reporter.repos_scanner import filter_repos_from_regexp, list_ecr_repos


def main():
    """Console script for ecr_scan_reporter."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", help="AWS Profile name to use for API Calls", required=False)
    parser.add_argument("--region", help="AWS Region to scan ECR Repos for", required=False)
    parser.add_argument(
        "--repos-regex",
        help="Regular expression to filter repositories names",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--duration-override",
        help="The time period expressed in m|w|d expressing the time delta to scan images from",
        required=False,
        default="7d",
    )
    parser.add_argument(
        "--no-scanning",
        action="store_true",
        default=False,
        help="Whether or not trigger a scan of the images identified",
    )
    parser.add_argument("_", nargs="*")
    args = parser.parse_args()

    if args.profile and args.region:
        cli_session = session.Session(profile_name=args.profile, region_name=args.region)
    elif args.profile and not args.region:
        cli_session = session.Session(profile_name=args.profile)
    elif not args.profile and args.region:
        cli_session = session.Session(region_name=args.region)
    else:
        cli_session = session.Session()

    print("Arguments: " + str(args._))
    account_region_repos = list_ecr_repos(ecr_session=cli_session)
    filtered_repos = filter_repos_from_regexp(account_region_repos, repos_names_filter=args.repos_regex)
    print("Repos found with provided parameters", filtered_repos)
    for repo in filtered_repos:
        print(f"Analyzing images of {repo}")
        scan_repo_images(
            repo, duration_override=args.duration_override, no_scan_images=args.no_scanning, ecr_session=cli_session
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
