
import json
import os
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape


BASE_DIR = os.path.abspath(os.path.dirname(__name__))
CODE_LINE = re.compile(r'(\d+) *(\w+|#|\'|\")')


def get_bandit_url(value):
    try:
        from bandit.core.docs_utils import get_url
        return get_url(value)
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


if __name__ == '__main__':
    import argparse
    import sys

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
    parser.add_argument("-b", "--base", dest="base_uri", type=str, default=None,
                        help="The URI for add on the base html tag")

    options = vars(parser.parse_args())

    report_json = json.load(open(options.get('report')[0]))

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
            parser.print_help()
            print("File {} not found".format(template_file))
            exit(-1)

    env = Environment(
        loader=FileSystemLoader(loader_fs),
        autoescape=select_autoescape(['html']),
    )
    env.filters['get_bandit_url'] = get_bandit_url
    env.filters['show_code'] = show_code
    template = env.get_template(template_file)

    stdout = sys.stdout
    if options.get('output'):
        stdout = open(options.get('output'), 'w')

    report = template.render(**report_json)
    stdout.write(report)
    if options.get('output'):
        stdout.close()
