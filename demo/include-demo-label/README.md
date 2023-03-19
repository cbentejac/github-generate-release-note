# Demo

Release note generated with the "demo" label excluded.

Cancelled pull requests like #9 are automatically ignored.

The pull request number is directly shown, and it is not necessary to hover over the link or to click it to see which pull request is referred to.

No pull request tagged with the label "demo" is included in the final release note. A "Demo Milestone-demo.md" file is output, listing all the pull requests with this label.

_Any file in this directory beside this README.md is a result of the command below._

```
./github-generate-release-note.py -o cbentejac -r github-generate-release-note -m "Demo Milestone" --pr-nb --label-exclude demo
```

