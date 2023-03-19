# bin module

## Prerequisites

`Python 3.x` must be installed, as well as the `requests` module:
```
pip install requests
```

## GitHub Pull Requests Exporter

The GitHub Pull Requests Exporter uses the GitHub API to request the list of closed pull requests associated to a specified repository's milestone.

The response to the requests is saved and exported into a JSON file, without any parsing.

The request can contain sorting information (in which order the request should be answered) as well as a GitHub authentication token, which may be useful when many requests are sent to the GitHub API.

Pagination is handled by the script: if the response spans over more than a single page (if the number of elements exceeds 100), the Exporter will send additional requests to retrieve the content over all the pages. As such, the Exporter sends at most $ceil(pullRequestsNb / 100)$ requests to the GitHub API.

### Usage

```
./github_export_pull_requests.py [-h] -o OWNER -r REPO -m MILESTONE
                                 [-s {created-desc,created-asc,comments-desc,comments-asc,updated-desc,updated-asc,relevance-desc}]
                                 [--output OUTPUT] [-t TOKEN]
```

### Options description

`-o OWNER, --owner OWNER`: owner of the GitHub repository to extract the information from

`-r REPO, --repo REPO`: name of the GitHub repository to extract the information from

`-m MILESTONE, --milestone MILESTONE`: name of the milestone to extract the information with

`-s {created-desc,created-asc,comments-desc,comments-asc,updated-desc,updated-asc,relevance-desc}, --sort {created-desc,created-asc,comments-desc,comments-asc,updated-desc,updated-asc,relevance-desc}`: sort the pull requests in the requested order (default: updated-desc): 
- newest (created-desc)
- oldest (created-asc)
- most commented (comments-desc)
- least commented (comments-asc)
- recently updated (updated-desc)
- least recently updated (updated-asc)
- best match (relevance-desc)

`--output OUTPUT`: filename for the output JSON file (default: githublist.json)

`-t TOKEN, --token TOKEN`: GitHub authentication token (optional: might be needed to perform a lot of requests in a short amount of time)

## Release Note Formatter

The Release Note Formatter parses a JSON file containing the GitHub's response to a request for a list of pull requests associated to a milestone, and generates a release note based on this information.

The release note that is generated is written as a markdown file, named `[milestone]-release-note.md` with `[milestone]` being the name of the milestone (e.g. for a milestone named "v1.0.0", the generated release note will be named `v1.0.0-release-note.md`).

It lists all the merged pull requests, in the order specified at the moment of the request, and automatically ignores pull requests that were cancelled (closed but not merged). The list of contributors (users that have opened at least one pull request that was merged), sorted by alphabetical order, can be generated in a separated markdown file named `[milestone]-authors.md`.

GitHub labels associated to the pull requests and words included in the pull requests' names can be filtered in (included) or out (excluded) the release note.

If they are included, they will be separated from the main list and displayed in their own subsection in the `[milestone]-release-note.md` file. If they are excluded, they will not be present at all in the final release note, but will instead be output in separate markdown files, listing the pull requests that specifically fitted the labels or words to exclude.

### Usage

```
./format_release_note.py [-h] [-i INPUT] [--authors] [--pr-nb] [--label-exclude EXCLUDE [EXCLUDE ...]]
                         [--label-include INCLUDE [INCLUDE ...]] [--word-exclude WORD_EXCLUDE [WORD_EXCLUDE ...]]
                         [--word-include WORD_INCLUDE [WORD_INCLUDE ...]]
```

### Options

`-i INPUT, --input INPUT`: path of the file to parse and format (default: githublist.json) 

`--authors`: save the list of pull requests authors in a dedicated file

`--pr-nb`: include the merged pull requests' number with their link

`--label-exclude EXCLUDE [EXCLUDE ...]`: labels that will be excluded from the release note and dumped in a dedicated file instead; several labels can be provided at once, either concatenated like "--label-exclude label1,label2" to dump them in the same file, or separated like "--label-exclude label1 label2" to dump them in separate files. a pull request does not need to have all the labels from a concatenated input to be excluded, one is enough. labels are case-sensitive. label exclusion takes precedence over word exclusion.

`--label-include INCLUDE [INCLUDE ...]`: labels that will be included in the release note but in a subsection; several labels can be provided at once, either concatenated like "--label-include label1,label2" to place them in the same subsection, or separated like "--label-include label1 label2" to place them in different subsections. a pull request does not need to have all the labels from a concatenated input to be separated from the main release note, one is enough. labels are case-sensitive. label inclusion takes precedence over word inclusion.

`--word-exclude WORD_EXCLUDE [WORD_EXCLUDE ...]`: words in the title of the pull requests that will be excluded from the release note and dumped in a dedicated file instead; several words can be provided at once, either concatenated like "--word-exclude word1,word2" to dump them in the same file, or separated like "--word-exclude word1,word2" to dump them in separate files. a pull request does not need to have all the words from a concatenated input in its title to be excluded, one is enough. words are case-insensitive. word exclusion is not prioritary over label exclusion.

`--word-include WORD_INCLUDE [WORD_INCLUDE ...]`: words in the title of the pulls requests that will be included in the release note but in a subsection; several words can be provided at once, either concatenated like "--word-include word1,word2" to place them in the same subsection, or separated like "--word-include label1 label2" to place them in different subsections. a pull request does not need to have all the words from a concatenated input in its title to be separated from the main release note, one is enough. words are case-insensitive. word inclusion is not prioritary over label inclusion.
