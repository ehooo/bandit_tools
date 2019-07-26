# Bandit Tools [![Build Status](https://travis-ci.org/ehooo/bandit_tools.svg)](https://travis-ci.org/ehooo/bandit_tools)
List of apps designed to help Bandit users

## custom_report.py
`python -m bandit_tools.custom_report`
```
usage: bandit_custom_report [-h] [-o OUTPUT] [-p TEMPLATE_PATH] [-t TEMPLATE]
                        [-b BASE_URI]
                        report

Tool for Bandit Custom HTML report This tools allows to create a customize
HTML Bandit from json one using Jinja2 to compose the HTML

positional arguments:
  report                the report on JSON format

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file
  -p TEMPLATE_PATH, --path TEMPLATE_PATH
                        The template path where files will be storage
  -t TEMPLATE, --template TEMPLATE
                        Template to render by default my_report.html
  -b BASE_URI, --base BASE_URI
                        The URI for add on the base html tag
```

## baseline_tools.py
`python -m bandit_tools.baseline_tools`
```
usage: baseline_tools [-h] [-z] [-f] [-M] [-m MIXED] [-o OUTPUT] baseline

Tool for Bandit baseline

positional arguments:
  baseline              baseline file work with

optional arguments:
  -h, --help            show this help message and exit
  -z, --zip             Minimize the result, remove all 0 hits files
  -f, --fix             Fix format and data on manual json files
  -M, --machine         Json format without indent
  -m MIXED, --mixed MIXED
                        second baseline mixed with
  -o OUTPUT, --output OUTPUT
                        output file
```
* `--fix`

The fix option will be recalculate the "_total" field on "metrics"
and order the "results" field.

* `--mix`

The mix option will be recived a second `report.json` and
calculate the new file with `baseline + report.json`
so new "_total" field on "metrics" will be created with proper information

### KNOWN ISSUES
If you have the same risky code on two lines in the same file, the `--mix`
option will be remove one of them, cause it is detected as duplicated hit. 
