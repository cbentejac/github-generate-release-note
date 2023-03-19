#!/usr/bin/env python

import argparse
import requests
from requests.exceptions import RequestException
import json


def setup_arg_parser():
    """ Initialize the argument parser and set the list of arguments. """

    arg_parser = argparse.ArgumentParser(
        description="""Tool to export the full list of pull requests associated
                       to a milestone for a specified GitHub repository as a
                       JSON file.""")
    arg_parser.add_argument(
        "-o", "--owner",
        required=True,
        help="owner of the GitHub repository to extract the information from")
    arg_parser.add_argument(
        "-r", "--repo",
        required=True,
        help="name of the GitHub repository to extract the information from")
    arg_parser.add_argument(
        "-m", "--milestone",
        required=True,
        help="name of the milestone to extract the information with")
    arg_parser.add_argument(
        "-s", "--sort",
        choices=["created-desc", "created-asc", "comments-desc",
                 "comments-asc", "updated-desc", "updated-asc",
                 "relevance-desc"],
        default="updated-desc",
        help="""sort the pull requests in the requested order 
                (default: updated-desc): newest (created-desc),
                oldest (created-asc), most commented (comments-desc),
                least commented (comments-asc),
                recently updated (updated-desc),
                least recently updated (updated-asc),
                best match (relevance-desc)""")
    arg_parser.add_argument(
        "--output",
        default="githublist.json",
        help="filename for the output JSON file (default: githublist.json)")
    arg_parser.add_argument(
        "-t", "--token",
        help="""GitHub authentication token (optional: might be needed to 
                perform a lot of requests in a short amount of time)""")

    return arg_parser


def request_pull_requests(repository, milestone, sorting, token):
    """ Send the request to retrieve all the pull requests associated to a
        a milestone for a given repository and catch the response. If there
        are several pages, retrieve them all and concatenate while preserving
        the sorting order. """

    GITHUB_REQUEST_URL = "https://api.github.com/search/issues"
    TYPE_PR_REQUEST = "type:pr"
    STATE_CLOSED_REQUEST = "state:closed"

    requested_parameters = "?q={}+{}+{}+{}+{}".format(
        milestone, TYPE_PR_REQUEST, STATE_CLOSED_REQUEST, repository, sorting)
    request_url = "{}{}".format(GITHUB_REQUEST_URL, requested_parameters)

    # Set the number of results on a page to 100 to reduce the number of pages
    # GitHub sets it to 30 by default
    REQUESTS_PER_PAGE = 100
    page = 1  # Start with the first page
    extra_parameters = {"page": page, "per_page": REQUESTS_PER_PAGE}

    header = {}
    if token:
        header["Authorization"] = "token {}".format(token)

    pull_requests = {}

    while True:
        response = requests.get(
            request_url, headers=header, params=extra_parameters)

        # Check response's status code
        code = response.status_code
        if code != 200:
            if code == 404:
                print("Error 404: page not found.")
            else:
                print(response.json().get("message"))
            response.raise_for_status()

        # Save the response & concatenate it with the previous pages (if any)
        # The specified sorting order will preserved
        if not pull_requests:
            pull_requests = response.json()
        else:
            pull_requests["items"].extend(response.json()["items"])

        # Go to the next page (if any)
        link = response.headers.get("Link", False)
        if link and 'rel="next"' in link:
            page = page + 1
            extra_parameters["page"] = page
        else:
            break

    return pull_requests


def execute(repo_param, milestone_param, sorting_param, token, output):
    try:
        pull_requests = request_pull_requests(
            repo_param, milestone_param, sorting_param, token)
    except RequestException as _:
        print("Exception while trying to access GitHub")
        return

    with open("{}".format(output), "w", encoding="utf8") as json_file:
        json.dump(pull_requests, json_file, indent=4)


def main():
    arg_parser = setup_arg_parser()
    args = arg_parser.parse_args()

    repo_param = "repo:{}/{}".format(args.owner, args.repo)
    if args.milestone.strip().find(' ') == -1:
        milestone_param = "milestone:{}".format(args.milestone)
    else:
        milestone_param = "milestone:\"{}\"".format(args.milestone)
    sorting_param = "sort:{}".format(args.sort)

    execute(repo_param, milestone_param,
            sorting_param, args.token, args.output)


if __name__ == "__main__":
    main()
