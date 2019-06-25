from bandit_tools.baseline_tools import BanditReport
from bandit_tools.baseline_tools import BASE_DICT
from bandit_tools.baseline_tools import main

import pytest

import argparse
import json
import sys
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class ExitMock(object):
    CALL_ARGS = None
    CALL_KWARGS = None

    def exit(self, *args, **kwargs):
        self.CALL_ARGS = args
        self.CALL_KWARGS = kwargs
        raise SystemExit()


def test_bandit_report_get_hash():
    hash_funct = BanditReport.get_hash
    ordered_keys = {'a': 'A', 'b': 'B'}
    unordered_keys = {'b': 'B', 'a': 'A'}
    assert hash_funct(ordered_keys) == hash_funct(unordered_keys)
    assert hash_funct(ordered_keys) != hash_funct({'b': 'A', 'a': 'B'})


def test_bandit_report_get_hash_similar_code():
    hash_funct = BanditReport.get_hash
    similar1 = {
        "filename": "examples/example_system.py",
        "issue_confidence": "MEDIUM",
        "issue_severity": "MEDIUM",
        "code": "3 import os, sys\n4 os.system(sys.argsv[1])\n5 print('Done')\n",
        "line_number": 4,
        "line_range": [
            4
        ],
    }
    similar2 = {
        "filename": "examples/example_system.py",
        "issue_confidence": "MEDIUM",
        "issue_severity": "MEDIUM",
        "code": "13 import os, sys\n14 os.system(sys.argsv[1])\n15 print('Done')\n",
        "line_number": 14,
        "line_range": [
            14
        ],
    }
    assert hash_funct(similar1) == hash_funct(similar2)
    similar2["filename"] = "examples/example_system2.py"
    assert hash_funct(similar1) != hash_funct(similar2)


def test_bandit_report_metric_emtpy():
    report = BanditReport()
    assert report.metrics == {"_totals": BASE_DICT}


def test_bandit_report_metric_with_one_file():
    report = BanditReport()
    report.add_file('filename', 100, 10)
    new_metric = BASE_DICT.copy()
    new_metric['loc'] = 100
    new_metric['nosec'] = 10
    expected = {
        "_totals": new_metric,
        'filename': new_metric
    }
    assert report.metrics == expected


def test_bandit_report_metric_with_two_files():
    report = BanditReport()
    report.add_file('filename1', 100, 10)

    new_metric1 = BASE_DICT.copy()
    new_metric1['loc'] = 100
    new_metric1['nosec'] = 10

    report.add_file('filename2', 50, 5)
    new_metric2 = BASE_DICT.copy()
    new_metric2['loc'] = 50
    new_metric2['nosec'] = 5

    total = BASE_DICT.copy()
    total['loc'] = 150
    total['nosec'] = 15

    expected = {
        "_totals": total,
        'filename1': new_metric1,
        'filename2': new_metric2,
    }
    assert report.metrics == expected


def test_bandit_report_metric_with_two_files_and_hits():
    report = BanditReport()
    report.add_file('filename1', 100, 10)
    report.add_hit({
        "issue_confidence": 'LOW',
        "issue_severity": 'MEDIUM',
        "filename": 'filename1'
    })
    new_metric1 = BASE_DICT.copy()
    new_metric1['loc'] = 100
    new_metric1['nosec'] = 10
    new_metric1["SEVERITY.MEDIUM"] = 1
    new_metric1["CONFIDENCE.LOW"] = 1

    report.add_file('filename2', 50, 5)
    report.add_hit({
        "issue_confidence": 'HIGH',
        "issue_severity": 'MEDIUM',
        "filename": 'filename2'
    })
    new_metric2 = BASE_DICT.copy()
    new_metric2['loc'] = 50
    new_metric2['nosec'] = 5
    new_metric2["SEVERITY.MEDIUM"] = 1
    new_metric2["CONFIDENCE.HIGH"] = 1

    total = BASE_DICT.copy()
    total['loc'] = 150
    total['nosec'] = 15
    total["SEVERITY.MEDIUM"] = 2
    total["CONFIDENCE.LOW"] = 1
    total["CONFIDENCE.HIGH"] = 1

    expected = {
        "_totals": total,
        'filename1': new_metric1,
        'filename2': new_metric2,
    }
    assert report.metrics == expected


def test_bandit_report_metric_same_file():
    report = BanditReport()
    report.add_file('filename', 100, 10)
    report.add_file('filename', 100, 10)

    new_metric = BASE_DICT.copy()
    new_metric['loc'] = 100
    new_metric['nosec'] = 10

    expected = {
        "_totals": new_metric,
        'filename': new_metric,
    }
    assert report.metrics == expected


def test_bandit_report_metric_same_file_different_lines():
    report = BanditReport()
    report.add_file('filename', 100, 10)
    report.add_file('filename', 50, 10)

    report.use_mix_data = False
    with pytest.raises(ValueError):
        report.add_file('filename', 50, 10)

    new_metric = BASE_DICT.copy()
    new_metric['loc'] = 100
    new_metric['nosec'] = 10

    expected = {
        "_totals": new_metric,
        'filename': new_metric,
    }
    assert report.metrics == expected


def test_bandit_report_metric_same_file_different_nosec():
    report = BanditReport()
    report.add_file('filename', 100, 10)
    report.add_file('filename', 100, 5)

    report.use_mix_data = False
    with pytest.raises(ValueError):
        report.add_file('filename', 100, 5)

    new_metric = BASE_DICT.copy()
    new_metric['loc'] = 100
    new_metric['nosec'] = 10

    expected = {
        "_totals": new_metric,
        'filename': new_metric,
    }
    assert report.metrics == expected


def test_bandit_report_same_hit():
    report = BanditReport()
    report.add_file('filename', 100, 10)
    report.add_hit({
        "issue_confidence": 'LOW',
        "issue_severity": 'MEDIUM',
        "filename": 'filename'
    })
    report.add_hit({
        "issue_confidence": 'LOW',
        "issue_severity": 'MEDIUM',
        "filename": 'filename'
    })
    new_metric = BASE_DICT.copy()
    new_metric['loc'] = 100
    new_metric['nosec'] = 10
    new_metric["SEVERITY.MEDIUM"] = 1
    new_metric["CONFIDENCE.LOW"] = 1

    expected = {
        "_totals": new_metric,
        'filename': new_metric,
    }
    assert report.metrics == expected


def test_bandit_report_add_hit_to_no_existed_file():
    report = BanditReport()
    with pytest.raises(KeyError):
        report.add_hit({
            "issue_confidence": 'LOW',
            "issue_severity": 'MEDIUM',
            "filename": 'filename'
        })


def test_main_no_args(monkeypatch):
    exit_mock = ExitMock()
    monkeypatch.setattr(argparse.ArgumentParser, "exit", exit_mock.exit)
    with pytest.raises(SystemExit):
        main()
    assert len(exit_mock.CALL_ARGS) == 2
    assert exit_mock.CALL_ARGS[0] == 2
    expected_msg = 'the following arguments are required: baseline'
    if sys.version_info.major == 2:
        expected_msg = 'too few arguments'
    assert exit_mock.CALL_ARGS[1].endswith('error: {}\n'.format(expected_msg))
    assert exit_mock.CALL_KWARGS == {}


def test_main_file_not_exist(monkeypatch):
    exit_mock = ExitMock()
    monkeypatch.setattr(argparse.ArgumentParser, "exit", exit_mock.exit)
    invalid_file = os.path.join(BASE_PATH, 'not_exist_file.json')
    monkeypatch.setattr(sys, "argv", ['app.py', invalid_file])

    with pytest.raises(SystemExit):
        main()
    assert len(exit_mock.CALL_ARGS) == 2
    assert exit_mock.CALL_ARGS[0] == -2
    expected_msg = "File {} not found".format(invalid_file)
    assert exit_mock.CALL_ARGS[1] == expected_msg
    assert exit_mock.CALL_KWARGS == {}


def test_main_zip(monkeypatch):
    out_file = os.path.join(BASE_PATH, 'test_report.json')
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'report_example.json'),
                                      '--zip', '--output', out_file])
    main()
    try:
        report = json.load(open(out_file))
        assert "examples/__init__.py" not in report.get('metrics', {})
    finally:
        os.remove(out_file)


def test_main_machine(monkeypatch):
    out_file = os.path.join(BASE_PATH, 'test_report.json')
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'report_example.json'),
                                      '--machine', '--output', out_file])
    main()

    try:
        assert "\n" not in open(out_file).read()
    finally:
        os.remove(out_file)


def test_main_fix(monkeypatch):
    out_file = os.path.join(BASE_PATH, 'test_report.json')
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'manual_report_example.json'),
                                      '--fix', '--output', out_file])
    main()

    try:
        report = json.load(open(out_file))
        assert "examples/__init__.py" in report.get('metrics', {})
        totals = report.get('metrics', {}).get('_totals', {})

        assert totals.get("nosec") == 0
        assert totals.get("loc") == 5
        assert totals.get("SEVERITY.UNDEFINED") == 0
        assert totals.get("SEVERITY.HIGH") == 0
        assert totals.get("SEVERITY.MEDIUM") == 1
        assert totals.get("SEVERITY.LOW") == 1
        assert totals.get("CONFIDENCE.UNDEFINED") == 0
        assert totals.get("CONFIDENCE.HIGH") == 1
        assert totals.get("CONFIDENCE.MEDIUM") == 1
        assert totals.get("CONFIDENCE.LOW") == 0

        hits = report.get('results', [{}, {}])
        assert hits[0].get('filename') == "examples/assert.py"
        assert hits[1].get('filename') == "examples/binding.py"

    finally:
        os.remove(out_file)


def test_main_mix_file_not_exit(monkeypatch):
    out_file = os.path.join(BASE_PATH, 'test_report.json')
    invalid_file = os.path.join(BASE_PATH, 'not_exist_file.json')
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'manual_report_example.json'),
                                      '--mixed', invalid_file,
                                      '--output', out_file])
    exit_mock = ExitMock()
    monkeypatch.setattr(argparse.ArgumentParser, "exit", exit_mock.exit)

    with pytest.raises(SystemExit):
        main()
    assert len(exit_mock.CALL_ARGS) == 2
    assert exit_mock.CALL_ARGS[0] == -3
    expected_msg = "File {} not found".format(invalid_file)
    assert exit_mock.CALL_ARGS[1] == expected_msg
    assert exit_mock.CALL_KWARGS == {}


def test_main_mix_file(monkeypatch):
    out_file = os.path.join(BASE_PATH, 'test_report.json')
    mix_file = os.path.join(BASE_PATH, 'mix_report_example.json')
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'manual_report_example.json'),
                                      '--mixed', mix_file,
                                      '--output', out_file])
    main()
    try:
        mixed_report = json.load(open(out_file))
        keys = mixed_report.get('metrics', {}).keys()
        assert "examples/__init__.py" in keys
        assert "examples/assert.py" in mixed_report.get('metrics', {}).keys()
        assert "examples/binding.py" in mixed_report.get('metrics', {}).keys()
        assert "examples/assert.py" in mixed_report.get('metrics', {}).keys()
        assert "examples/django_sql_injection_extra.py" in mixed_report.get('metrics', {}).keys()
        assert "examples/django_sql_injection_raw.py" in mixed_report.get('metrics', {}).keys()
        assert "examples/eval.py" in mixed_report.get('metrics', {})

        totals = mixed_report.get('metrics', {}).get('_totals')
        assert totals.get("CONFIDENCE.HIGH") == 4
        assert totals.get("CONFIDENCE.LOW") == 0
        assert totals.get("CONFIDENCE.MEDIUM") == 16
        assert totals.get("CONFIDENCE.UNDEFINED") == 0
        assert totals.get("SEVERITY.HIGH") == 0
        assert totals.get("SEVERITY.LOW") == 1
        assert totals.get("SEVERITY.MEDIUM") == 19
        assert totals.get("SEVERITY.UNDEFINED") == 0
        assert totals.get("loc") == 50
        assert totals.get("nosec") == 1

    finally:
        os.remove(out_file)
