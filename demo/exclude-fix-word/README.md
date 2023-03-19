# Demo

Release note generated with the word "[FIX]" excluded.

Cancelled pull requests like #9 are automatically ignored.

The pull request number is directly shown, and it is not necessary to hover over the link or to click it to see which pull request is referred to.

All the pull requests containing the word "[FIX]" (not case-sensitive) in their title are not part of the final release note, but are dumped in a dedicated "Demo Milestone-[fix].md" file.

_Any file in this directory beside this README.md is a result of the command below._

```
./github-generate-release-note.py -o cbentejac -r github-generate-release-note -m "Demo Milestone" --pr-nb --word-exclude [FIX]
```

