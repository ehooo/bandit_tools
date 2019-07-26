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
import json
import os
import sys
import hashlib
import datetime
import operator
import re

CODE_LINE = re.compile(r'(\d+) *(\w+|#|\'|\")')
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
BASE_DICT = {
    "loc": 0,  # Lines Of Code
    "nosec": 0,  # Number of nosec comments
    "CONFIDENCE.HIGH": 0,
    "CONFIDENCE.MEDIUM": 0,
    "CONFIDENCE.LOW": 0,
    "CONFIDENCE.UNDEFINED": 0,
    "SEVERITY.HIGH": 0,
    "SEVERITY.MEDIUM": 0,
    "SEVERITY.LOW": 0,
    "SEVERITY.UNDEFINED": 0,
}


def zip_report(report):
    metrics = report["metrics"].copy()
    for filename in report["metrics"]:
        hits = 0
        for key in report["metrics"][filename]:
            if not (key in ["loc", "nosec"]):
                hits += report["metrics"][filename][key]
        if not hits:
            del (metrics[filename])
    zip_baseline = report.copy()
    zip_baseline["metrics"] = metrics
    return zip_baseline


def filter_code(value):
    lines = []
    tab = ' '
    for line in value.split('\n'):
        line = line.replace('\t', ' ')
        m = CODE_LINE.match(line)
        if m:
            (num, word) = m.groups()
            pos = line.find(word)
            code = line[pos:]
            line = tab
            line += code
            lines.append(line)
        else:
            lines.append(line)

    code = '\n'.join(lines)
    return code.encode('utf8')


class BanditReport(object):

    def __init__(self):
        self.errors = []
        self._result = []
        self._metrics = {}
        self._hist = {}
        self._hist_hash = []
        self.use_mix_data = True
        self.ignore_lines = True

    @staticmethod
    def get_hash(hit_data, ignore_lines=True):
        h = hashlib.md5()
        keys = hit_data.keys()
        for key in sorted(keys):
            if key == 'code':
                h.update(filter_code(hit_data[key]))
            elif key in ['line_number', 'line_range']:
                if not ignore_lines:
                    h.update(str(hit_data[key]).encode('utf8'))
            else:
                h.update(hit_data[key].encode('utf8'))
        return h.hexdigest()

    @property
    def metrics(self):
        metrics = {
            "_totals": BASE_DICT.copy()
        }
        for filename in self._metrics.keys():
            metrics[filename] = self._metrics[filename]
            for key in self._metrics[filename]:
                metrics["_totals"][key] += self._metrics[filename][key]
        return metrics

    def to_dict(self):
        return {
            'metrics': self.metrics,
            'generated_at': self.generated_at,
            'errors': self.errors,
            'results': sorted(self._result, key=operator.itemgetter('filename'))
        }

    def add_hit(self, result):
        hit_hash = BanditReport.get_hash(result, self.ignore_lines)
        if hit_hash in self._hist_hash:
            return
        self._hist_hash.append(hit_hash)

        conf_key = "CONFIDENCE.{}".format(result["issue_confidence"])
        sev_key = "SEVERITY.{}".format(result["issue_severity"])

        filename = result["filename"]
        file_data = self._metrics[filename]
        file_data[conf_key] += 1
        file_data[sev_key] += 1

        self._result.append(result)

    def add_file(self, filename, lines_of_code, num_nosec):
        if filename in self._metrics:
            lines = bool(self._metrics[filename]['loc'] != lines_of_code)
            nosec = bool(self._metrics[filename]['nosec'] != num_nosec)
            if not self.use_mix_data and (lines or nosec):
                raise ValueError('The file has been entered before with other data')
            return
        self._metrics[filename] = BASE_DICT.copy()
        self._metrics[filename]['loc'] = lines_of_code
        self._metrics[filename]['nosec'] = num_nosec

    @property
    def generated_at(self):
        return datetime.datetime.utcnow().strftime(TS_FORMAT)


def mix_report(base, other):
    generator = BanditReport()
    for report in [base, other]:
        for filename in report['metrics']:
            if filename != "_totals":
                lines_of_code = report['metrics'][filename]['loc']
                num_nosec = report['metrics'][filename]['nosec']
                generator.add_file(filename, lines_of_code, num_nosec)
        for hit in report['results']:
            generator.add_hit(hit)
    return generator.to_dict()


def fix(report):
    generator = BanditReport()
    generator.ignore_lines = False
    for filename in report['metrics']:
        if filename != "_totals":
            lines_of_code = report['metrics'][filename]['loc']
            num_nosec = report['metrics'][filename]['nosec']
            generator.add_file(filename, lines_of_code, num_nosec)
    for hit in report['results']:
        generator.add_hit(hit)
    return generator.to_dict()


def main():
    parser = argparse.ArgumentParser(description='Tool for Bandit baseline')

    parser.add_argument("baseline", type=str, nargs=1,
                        help="baseline file work with")
    parser.add_argument("-z", "--zip", dest="zip", default=False, action="store_true",
                        help="Minimize the result, remove all 0 hits files")
    parser.add_argument("-f", "--fix", dest="fix", default=False, action="store_true",
                        help="Fix format and data on manual json files")
    parser.add_argument("-M", "--machine", dest="machine", default=False, action="store_true",
                        help="Json format without indent")
    parser.add_argument("-m", "--mixed", dest="mixed", type=str, help="second baseline mixed with")
    parser.add_argument("-o", "--output", dest="output", type=str, help="output file", default=None)

    options = vars(parser.parse_args())

    valid_file = options.get('baseline', [""])[0]
    if not os.path.isfile(valid_file):
        parser.exit(-2, "File {} not found".format(valid_file))
    baseline = json.load(open(valid_file))

    valid_file = options.get('mixed')
    if valid_file:
        if not os.path.isfile(valid_file):
            parser.exit(-3, "File {} not found".format(valid_file))
        mixed_to = json.load(open(valid_file))
        baseline = mix_report(baseline, mixed_to)

    if options.get('zip'):
        baseline = zip_report(baseline)

    if options.get('fix'):
        baseline = fix(baseline)

    indent = None if options.get('machine') else 2
    json_str = json.dumps(baseline, sort_keys=True, indent=indent, separators=(',', ': '))

    stdout = sys.stdout
    if options.get('output'):
        stdout = open(options.get('output'), 'w')

    stdout.write(json_str)
    if options.get('output'):
        stdout.close()


if __name__ == '__main__':  # pragma: no cover
    main()
