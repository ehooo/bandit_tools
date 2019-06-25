# -*- coding: utf-8 -*-
"""
Copyright 2019 Victor Torre

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import sys
import json
import os
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_LINE = re.compile(r'(\d+) *(\w+|#|\'|\")')
VALID_BASE_URI = re.compile(r'^((https?|file)://|/)')

BANDIT_URLS = {}  # To fix bug https://github.com/PyCQA/bandit/issues/506


def get_bandit_url(value):
    try:
        from bandit.core.docs_utils import get_url
        global BANDIT_URLS
        if value not in BANDIT_URLS:
            BANDIT_URLS[value] = get_url(value)
        return BANDIT_URLS[value]
    except ImportError:
        return ''


def show_code(value, num_space=4):
    lines = []
    tab = str(' ' * num_space)
    for line in value.split('\n'):
        line = line.replace('\t', ' ')
        m = CODE_LINE.match(line)
        if m:
            (num, word) = m.groups()
            pos = line.find(word)
            code = line[pos:]
            line = num
            line += tab
            line += code
            lines.append(line)
        else:
            lines.append(line)
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Tool for Bandit Custom HTML report\n'
                    'This tools allows to create a customize HTML Bandit from json one'
                    ' using Jinja2 to compose the HTML'
    )

    parser.add_argument("report", type=str, nargs=1,
                        help="the report on JSON format")
    parser.add_argument("-o", "--output", type=str, help="output file", default=None)
    parser.add_argument("-p", "--path", dest="template_path", type=str, default=None,
                        help="The template path where files will be storage")
    parser.add_argument("-t", "--template", dest="template", type=str, default='my_report.html',
                        help="Template to render by default my_report.html")
    parser.add_argument("-b", "--base", dest="base_uri", type=str, default='',
                        help="The URI for add on the base html tag")

    options = vars(parser.parse_args())

    report_file = options.get('report')[0]
    if not os.path.isfile(report_file):
        parser.exit(-1, "File {} not found".format(report_file))

    report_json = json.load(open(report_file))

    loader_fs = []

    default_path = os.path.join(BASE_DIR, 'templates')
    if default_path and os.path.isdir(default_path):
        loader_fs.append(default_path)

    template_path = options.get('template_path')
    if template_path and os.path.isdir(template_path):
        loader_fs.append(template_path)

    template_file = options.get('template')
    if template_file:
        valid_file = False
        for path in loader_fs:
            check_file = os.path.join(path, template_file)
            if os.path.isfile(check_file):
                valid_file = True
                break
        if not valid_file:
            parser.exit(-2, "File {} not found".format(template_file))

    env = Environment(
        loader=FileSystemLoader(loader_fs),
        autoescape=select_autoescape(['html', 'jinja2', 'j2']),
    )
    env.filters['get_bandit_url'] = get_bandit_url
    env.filters['show_code'] = show_code
    template = env.get_template(template_file)

    base_uri = options.get('base_uri')
    if not VALID_BASE_URI.match(base_uri):
        base_uri = ''
    else:
        if not base_uri.endswith('/'):
            base_uri += '/'
        if base_uri.startswith('/'):
            base_uri = 'file://' + base_uri

    stdout = sys.stdout
    if options.get('output'):
        stdout = open(options.get('output'), 'w')

    report = template.render(base_uri=base_uri, **report_json)
    if sys.version_info.major == 2:  # pragma: no cover
        report = report.encode('utf8')
    stdout.write(report)
    if options.get('output'):
        stdout.close()


if __name__ == '__main__':  # pragma: no cover
    main()
