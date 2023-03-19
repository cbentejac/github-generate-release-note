# github-generate-release-note

github-generate-release-note is a tool to automatically generate a well-formatted release note containing all the merged pull requests from any GitHub repository's milestone.

Using GitHub's API, the list of closed pull requests associated to a milestone is retrieved and parsed to generate a markdown file that shows the merged pull requests' titles and links. Cancelled pull requests (closed pull requests that were never merged, but are still part of GitHub's response) are simply ignored.

The list of contributors (users who opened at least one pull request associated to the milestone) can be generated in a separate file.

Labels associated to the pull requests and words containing in the pull requests' titles can be filtered in or filtered out. If they are filtered in, they will be in the release note but separated from the main list of pull requests; instead, they will be shown in their own subsection. If they are filtered out, they will not appear in the release note but will be dumped in separated markdown files, named after the label or word to exclude.

## Prerequisites

`Python 3.x` must be installed, as well as the `requests` module:
```
pip install requests
```

## Usage

```
github-generate-release-note.py [-h] -o OWNER -r REPO -m MILESTONE
                                [-s {created-desc,created-asc,comments-desc,comments-asc,updated-desc,updated-asc,relevance-desc}]
                                [-t TOKEN] [--authors] [--pr-nb] [--label-exclude EXCLUDE [EXCLUDE ...]]
                                [--label-include INCLUDE [INCLUDE ...]]
                                [--word-exclude WORD_EXCLUDE [WORD_EXCLUDE ...]]
                                [--word-include WORD_INCLUDE [WORD_INCLUDE ...]] [--save]
```

## Options 

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

`-t TOKEN, --token TOKEN`: GitHub authentication token (optional: might be needed to perform a lot of requests in a short amount of time)

`--authors`: save the list of pull requests authors in a dedicated file

`--pr-nb`: include the merged pull requests' number with their link

`--label-exclude EXCLUDE [EXCLUDE ...]`: labels that will be excluded from the release note and dumped in a dedicated file instead; several labels can be provided at once, either concatenated like "--label-exclude label1,label2" to dump them in the same file, or separated like "--label-exclude label1 label2" to dump them in separate files. a pull request does not need to have all the labels from a concatenated input to be excluded, one is enough. labels are case-sensitive. label exclusion takes precedence over word exclusion.

`--label-include INCLUDE [INCLUDE ...]`: labels that will be included in the release note but in a subsection; several labels can be provided at once, either concatenated like "--label-include label1,label2" to place them in the same subsection, or separated like "--label-include label1 label2" to place them in different subsections. a pull request does not need to have all the labels from a concatenated input to be separated from the main release note, one is enough. labels are case-sensitive. label inclusion takes precedence over word inclusion.

`--word-exclude WORD_EXCLUDE [WORD_EXCLUDE ...]`: words in the title of the pull requests that will be excluded from the release note and dumped in a dedicated file instead; several words can be provided at once, either concatenated like "--word-exclude word1,word2" to dump them in the same file, or separated like "--word-exclude word1,word2" to dump them in separate files. a pull request does not need to have all the words from a concatenated input in its title to be excluded, one is enough. words are case-insensitive. word exclusion is not prioritary over label exclusion.

`--word-include WORD_INCLUDE [WORD_INCLUDE ...]`: words in the title of the pulls requests that will be included in the release note but in a subsection; several words can be provided at once, either concatenated like "--word-include word1,word2" to place them in the same subsection, or separated like "--word-include label1 label2" to place them in different subsections. a pull request does not need to have all the words from a concatenated input in its title to be separated from the main release note, one is enough. words are case-insensitive. word inclusion is not prioritary over label inclusion.

`--save`: do not remove the exported JSON file at the end of the process