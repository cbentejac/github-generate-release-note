#!/usr/bin/env python

from bin import github_export_pull_requests, format_release_note
import argparse
import os


def setup_arg_parser():
    """ Initialize the argument parser and set the list of arguments. """

    arg_parser = argparse.ArgumentParser(
        description="""Tool to generate a full release note based on all the 
                       GitHub pull requests associated to a milestone from a
                       repository. The release note will be output as a 
                       markdown file, containing only the list of pull requests
                       that were effectively merged (and not only closed). The 
                       list of pull requests' authors can be generated as well
                       in a separate file.""")
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
        "-t", "--token",
        help="""GitHub authentication token (optional: might be needed to 
                perform a lot of requests in a short amount of time)""")
    arg_parser.add_argument(
        "--authors",
        action="store_true",
        default=False,
        help="save the list of pull requests authors in a dedicated file")
    arg_parser.add_argument(
        "--pr-nb",
        dest="pr_nb",
        action="store_true",
        default=False,
        help="include the merged pull requests' number with their link")
    arg_parser.add_argument(
        "--label-exclude",
        dest="exclude",
        nargs="+",
        help="""labels that will be excluded from the release note and
                dumped in a dedicated file instead; several labels can be
                provided at once, either concatenated like
                "--label-exclude label1,label2" to dump them in the same file,
                or separated like "--label-exclude label1 label2" to dump
                them in separate files. a pull request does not need to have 
                all the labels from a concatenated input to be excluded, one is
                enough. labels are case-sensitive. label exclusion takes
                precedence over word exclusion.""")
    arg_parser.add_argument(
        "--label-include",
        dest="include",
        nargs="+",
        help="""labels that will be included in the release note but in a
                subsection; several labels can be provided at once, either
                concatenated like "--label-include label1,label2" to place
                them in the same subsection, or separated like
                "--label-include label1 label2" to place them in different
                subsections. a pull request does not need to have all the 
                labels from a concatenated input to be separated from the main
                release note, one is enough. labels are case-sensitive.
                label inclusion takes precedence over word inclusion.""")
    arg_parser.add_argument(
        "--word-exclude",
        dest="word_exclude",
        nargs="+",
        help="""words in the title of the pull requests that will be excluded 
                from the release note and dumped in a dedicated file instead;
                several words can be provided at once, either concatenated like
                "--word-exclude word1,word2" to dump them in the same file, or
                separated like "--word-exclude word1,word2" to dump them in
                separate files. a pull request does not need to have all the
                words from a concatenated input in its title to be excluded, 
                one is enough. words are case-insensitive. word exclusion
                is not prioritary over label exclusion.""")
    arg_parser.add_argument(
        "--word-include",
        dest="word_include",
        nargs="+",
        help="""words in the title of the pulls requests that will be included 
                in the release note but in a subsection; several words can be 
                provided at once, either concatenated like 
                "--word-include word1,word2" to place them in the same 
                subsection, or separated like "--word-include label1 label2" 
                to place them in different subsections. a pull request does 
                not need to have all the words from a concatenated input in its
                title to be separated from the main release note, one is 
                enough. words are case-insensitive. word inclusion is not 
                prioritary over label inclusion.""")
    arg_parser.add_argument(
        "--save",
        action="store_true",
        default=False,
        help="do not remove the exported JSON file at the end of the process")

    return arg_parser


def main():
    arg_parser = setup_arg_parser()
    args = arg_parser.parse_args()

    # Format the input parameters needed to issue the request
    repo_param = "repo:{}/{}".format(args.owner, args.repo)
    if args.milestone.strip().find(' ') == -1:
        milestone_param = "milestone:{}".format(args.milestone)
    else:
        milestone_param = "milestone:\"{}\"".format(args.milestone)
    sorting_param = "sort:{}".format(args.sort)

    # Name of the JSON file containing the data from GitHub
    json_file = "githublist.json"

    github_export_pull_requests.execute(
        repo_param, milestone_param, sorting_param, args.token, json_file)

    format_release_note.execute(json_file, args.authors, args.pr_nb,
                                args.exclude, args.include, args.word_exclude,
                                args.word_include)
    
    # Remove the JSON file containing the response from GitHub
    if not args.save:
        os.remove(json_file)


if __name__ == "__main__":
    main()
