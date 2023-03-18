#!/usr/bin/env python

import argparse
import json


def setup_arg_parser():
    """ Initialize the argument parser and set the list of arguments. """

    arg_parser = argparse.ArgumentParser(
        description="""Tool to format a JSON file obtained through the GitHub
                       API and containing the list of pull requests associated
                       to a milestone into a markdown release note. Pull
                       requests that were closed but not merged will be
                       automatically ignored. The list of contributors can be
                       generated in a separate files, and some labels may be
                       excluded from the final release note to be written in
                       separate files.""")
    arg_parser.add_argument(
        "-i", "--input",
        default="githublist.json",
        help="path of the file to parse and format (default: githublist.json)")
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
                them in separate files. a pull request do not need to have all 
                the labels from a concatenated input to be excluded, one is 
                enough.""")
    arg_parser.add_argument(
        "--label-include",
        dest="include",
        nargs="+",
        help="""labels that will be included in the release note but in a
                subsection; several labels can be provided at once, either
                concatenated like "--label-include label1,label2" to place
                them in the same subsection, or separated like
                "--label-include label1 label2" to place them in different
                subsections. a pull request do not need to have all the labels
                from a concatenated input to be separated from the main
                release note, one is enough.""")

    return arg_parser


def setup_labels_of_interest(labels_of_interest):
    """ Parse the provided labels to include/exclude, and distinguish cases
        where several labels need to be included/excluded separately or where
        they need to be included/excluded together. """

    relevant_labels = {}

    if labels_of_interest:
        for label in labels_of_interest:
            if "," in label:  # Identify concatenated labels, treat them as one
                concatenated_labels = label.split(",")
                relevant_labels[label] = concatenated_labels
            else:
                relevant_labels[label] = label

    return relevant_labels


def get_pr_labels(data):
    """ Get the list of the pull request's labels (if any). """

    labels = []
    pr_labels = data["labels"]
    if pr_labels:
        for label in pr_labels:
            labels.append(label["name"])
    return labels


def write_authors(authors, milestone_title):
    """ Write the file containing the list of the pull requests authors. """

    with open("{}-authors.md".format(milestone_title), "w",
              encoding="utf8") as authors_file:
        authors_file.write("## Contributors\n")
        for author in sorted(list(authors), key=str.casefold):
            authors_file.write("- {}\n".format(author))


def write_excluded_prs_note(excluded_pull_requests, milestone_title,
                            show_pr_nb):
    """ Write the files containing the excluded labels.
        Concatenated labels will be written in the same file together. """

    for excluded_labels, labeled_prs in excluded_pull_requests.items():
        # Remove characters that might cause issues with the filename
        filename = excluded_labels.replace(
            ":", "").replace("/", "").replace("?", "")

        with open("{}-{}.md".format(milestone_title, filename),
                  "w", encoding="utf8") as excluded_prs_file:
            excluded_prs_file.write("### {}\n\n".format(excluded_labels))
            for (title, link, number) in labeled_prs:
                excluded_prs_file.write(
                    "- {} [PR{}]({})\n".
                    format(title, " " + number if show_pr_nb else "", link))


def write_final_release_note(pull_requests, milestone_title,
                             included_pull_requests, show_pr_nb):
    """ Write the final release note containing all the pull requests that were
        correctly merged and not excluded because of their labels. Labels that
        are included will be written in a different subsection. """

    with open("{}-release-note.md".format(milestone_title),
              "w", encoding="utf8") as release_note:
        release_note.write("# Release note\n\n")
        release_note.write("## {}\n\n".format(milestone_title))
        for (title, link, number) in pull_requests:
            release_note.write("- {} [PR{}]({})\n"
                               .format(title,
                                       " " + number if show_pr_nb else "",
                                       link))
        for included_labels, labeled_prs in included_pull_requests.items():
            release_note.write("\n### {}\n\n".format(included_labels))
            for (title, link, number) in labeled_prs:
                release_note.write("- {} [PR{}]({})\n"
                                   .format(title,
                                           " " + number if show_pr_nb else "",
                                           link))


def main():
    arg_parser = setup_arg_parser()
    args = arg_parser.parse_args()

    with open("{}".format(args.input), "r") as json_file:
        data = json.load(json_file)

    # Check that there are pull requests to parse in the input file.
    # If the file does not directly come from the GitHub API, its structure
    # might be different and this tests will thus fail.
    pull_requests_data = data["items"]
    if len(pull_requests_data) == 0:
        print("No pull requests to parse in {}".format(args.input))
        return

    milestone_title = pull_requests_data[0]["milestone"]["title"]

    authors = set()  # Contains the username of contributors
    pull_requests = []  # Contains tuples (title, link, number)

    # Dictionary containing the excluded labels with a distinction
    # between concatenated labels and stand-alone ones
    excluded_labels = setup_labels_of_interest(args.exclude)

    # Initialize the dictionary of excluded pull requests based on their labels
    excluded_pull_requests = {}
    excluded_counters = {}
    for label in excluded_labels.keys():
        excluded_pull_requests[label] = []
        excluded_counters[label] = 0

    # Same thing for the included labels
    included_labels = setup_labels_of_interest(args.include)

    included_pull_requests = {}
    included_counters = {}
    for label in included_labels.keys():
        included_pull_requests[label] = []
        included_counters[label] = 0

    # Counters to print a summary at the end of the script
    total_counter = 0  # Pull requests in the input file
    regular_counter = 0  # Pull requests added to the final release note
    unmerged_counter = 0  # Pull requests closed but not merged

    for pr in pull_requests_data:
        total_counter = total_counter + 1

        # Ignore pulls requests that were closed but not merged
        merged = False if pr["pull_request"]["merged_at"] is None else True
        if not merged:
            unmerged_counter = unmerged_counter + 1
            continue

        # Update list of pull requests authors
        authors.add(pr["user"]["login"])

        # Get the labels from the pull request
        labels = get_pr_labels(pr)

        exclude_pr = False
        for label in labels:
            for excluded_label in excluded_labels.keys():
                if label in excluded_label:
                    excluded_pull_requests[excluded_label].append(
                        (pr["title"], pr["html_url"],
                            "#{}".format(pr["number"])))
                    excluded_counters[excluded_label] = \
                        excluded_counters[excluded_label] + 1
                    exclude_pr = True

        include_pr = False
        for label in labels:
            for included_label in included_labels.keys():
                if label in included_label:
                    included_pull_requests[included_label].append(
                        (pr["title"], pr["html_url"],
                            "#{}".format(pr["number"])))
                    included_counters[included_label] = \
                        included_counters[included_label] + 1
                    regular_counter = regular_counter + 1
                    include_pr = True

        if exclude_pr or include_pr:
            continue

        pull_requests.append(
            (pr["title"], pr["html_url"], "#{}".format(pr["number"])))
        regular_counter = regular_counter + 1

    print("==== Final Report ====")
    print("Total number of pull requests parsed: {}".format(total_counter))
    print("Total number of pull requests added to the release note: {}"
          .format(regular_counter))
    if included_counters:
        print("\tAmong which:")
        for label, counter in included_counters.items():
            print("\t- {} pull requests with the label(s) '{}'"
                  .format(counter, label))
    print("Total number of unique contributors: {}".format(len(authors)))
    print("Total number of unmerged pull requests that were ignored: {}"
          .format(unmerged_counter))
    print("Total number of excluded pull requests with the label(s):")
    for label, counter in excluded_counters.items():
        print("\t- '{}': {}".format(label, counter))

    if args.authors:
        write_authors(authors, milestone_title)
    write_final_release_note(
        pull_requests, milestone_title, included_pull_requests, args.pr_nb)
    if args.exclude:
        write_excluded_prs_note(excluded_pull_requests,
                                milestone_title, args.pr_nb)


if __name__ == '__main__':
    main()
