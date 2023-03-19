#!/usr/bin/env python

import argparse
import requests
from requests.exceptions import RequestException
import json

GITHUB_REQUEST_URL = "https://api.github.com/users/"


def setup_arg_parser():
    """ Initialize the argument parser and set the list of arguments. """

    arg_parser = argparse.ArgumentParser(
        description="""Tool to request, provided a JSON file containing a list 
                       of issues or pull requests, information about the 
                       authors of said issues or pull requests through the
                       GitHub API. The list of authors with their available
                       information will be output as a markdown file.""")
    arg_parser.add_argument(
        "--input",
        default="githublist.json",
        help="filename for the input JSON file (default: githublist.json)")
    arg_parser.add_argument(
        "-t", "--token",
        help="""GitHub authentication token (optional: might be needed to 
                perform a lot of requests in a short amount of time)""")

    return arg_parser


def request_author_info(username, token):
    """"""
    header = {}
    if token:
        header["Authorization"] = "token {}".format(token)

    request_url = "{}{}".format(GITHUB_REQUEST_URL, username)
    author_info = {}

    response = requests.get(request_url, headers=header, params={})

    # Check reponse's status code
    code = response.status_code
    if code != 200:
        if code == 404:
            print("Error 404: page not found")
        else:
            print(response.json().get("message"))
        response.raise_for_status()

    author_info = response.json()

    return author_info


def main():
    arg_parser = setup_arg_parser()
    args = arg_parser.parse_args()

    print(args.input)

    with open("{}".format(args.input), "r", encoding="utf8") as json_file:
        data = json.load(json_file)

    authors = set()

    data = data["items"]
    if len(data) == 0:
        print("Nothing to parse in {}".format(args.input))
        return

    for item in data:
        author = item["user"]["login"]
        if author not in authors:
            info = request_author_info(author, args.token)
            print(info)
            authors.add(author)
        else:
            print("Author already encountered, the information has already \
                  been retrieved.")



if __name__ == "__main__":
    main()
