import bandit
import bandit_tools.custom_report
import pytest

import argparse
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


def test_call_get_url(monkeypatch):
    bandit_tools.custom_report.BANDIT_URLS = {}

    def mock_get(*args, **kwargs):
        return "mock_url {}:{}".format(args, kwargs)
    monkeypatch.setattr(bandit.core.docs_utils, "get_url", mock_get)
    response = bandit_tools.custom_report.get_bandit_url('code')
    assert response == "mock_url ('code',):{}"


def test_call_get_url_exception(monkeypatch):
    bandit_tools.custom_report.BANDIT_URLS = {}

    def mock_get(*args, **kwargs):
        raise ImportError()

    monkeypatch.setattr(bandit.core.docs_utils, "get_url", mock_get, raising=False)
    response = bandit_tools.custom_report.get_bandit_url('code')
    assert response == ""


def test_show_code_empty():
    response = bandit_tools.custom_report.show_code('')
    assert response == ""


def test_show_code_no_match():
    response = bandit_tools.custom_report.show_code('line1\nline2')
    assert response == 'line1\nline2'


def test_show_code_match():
    response = bandit_tools.custom_report.show_code('1 line1\n2 line2')
    assert response == '1    line1\n2    line2'


def test_show_code_match_with_space():
    response = bandit_tools.custom_report.show_code('1 line1\n2 line2', num_space=2)
    assert response == '1  line1\n2  line2'


def test_main_no_args(monkeypatch):
    exit_mock = ExitMock()
    monkeypatch.setattr(argparse.ArgumentParser, "exit", exit_mock.exit)
    with pytest.raises(SystemExit):
        bandit_tools.custom_report.main()
    assert len(exit_mock.CALL_ARGS) == 2
    assert exit_mock.CALL_ARGS[0] == 2
    expected_msg = 'the following arguments are required: report'
    if sys.version_info.major == 2:
        expected_msg = 'too few arguments'
    assert exit_mock.CALL_ARGS[1].endswith('error: {}\n'.format(expected_msg))
    assert exit_mock.CALL_KWARGS == {}


def test_main_with_only_report_not_exist(monkeypatch):
    exit_mock = ExitMock()
    monkeypatch.setattr(argparse.ArgumentParser, "exit", exit_mock.exit)
    monkeypatch.setattr(sys, "argv", ['app.py', 'report'])
    with pytest.raises(SystemExit):
        bandit_tools.custom_report.main()
    assert len(exit_mock.CALL_ARGS) == 2
    assert exit_mock.CALL_ARGS[0] == -1
    assert exit_mock.CALL_ARGS[1] == 'File report not found'
    assert exit_mock.CALL_KWARGS == {}


def test_main_with_only_report_exist(monkeypatch):
    out_file = os.path.join(BASE_PATH, 'test_report.html')
    expected_file = os.path.join(BASE_PATH, 'report_example.html')
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'report_example.json'),
                                      '--output', out_file])
    bandit_tools.custom_report.main()

    try:
        assert open(out_file).read() == open(expected_file).read()
    finally:
        os.remove(out_file)


def test_main_without_path_exist(monkeypatch):
    out_file = os.path.join(BASE_PATH, 'test_report.html')
    expected_file = os.path.join(BASE_PATH, 'report_example.html')
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'report_example.json'),
                                      '--path', os.path.join(BASE_PATH, 'templates', 'no_exist'),
                                      '--output', out_file])
    bandit_tools.custom_report.main()

    try:
        assert open(out_file).read() == open(expected_file).read()
    finally:
        os.remove(out_file)


def test_main_with_path_but_no_template(monkeypatch):
    exit_mock = ExitMock()
    monkeypatch.setattr(argparse.ArgumentParser, "exit", exit_mock.exit)
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'report_example.json'),
                                      '--template', 'no_exist.html'])

    with pytest.raises(SystemExit):
        bandit_tools.custom_report.main()
    assert len(exit_mock.CALL_ARGS) == 2
    assert exit_mock.CALL_ARGS[0] == -2
    assert exit_mock.CALL_ARGS[1] == 'File no_exist.html not found'
    assert exit_mock.CALL_KWARGS == {}


def test_main_with_base_url(monkeypatch):
    out_file = os.path.join(BASE_PATH, 'test_report.html')
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'report_example.json'),
                                      '--path', os.path.join(BASE_PATH, '..', 'templates'),
                                      '--base', 'http://localhost/',
                                      '--output', out_file])
    bandit_tools.custom_report.main()

    try:
        assert '<base href = "http://localhost/"/>' in open(out_file).read()
    finally:
        os.remove(out_file)


def test_main_with_base_url_without_slash(monkeypatch):
    out_file = os.path.join(BASE_PATH, 'test_report.html')
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'report_example.json'),
                                      '--path', os.path.join(BASE_PATH, '..', 'templates'),
                                      '--base', 'http://localhost',
                                      '--output', out_file])
    bandit_tools.custom_report.main()

    try:
        assert '<base href = "http://localhost/"/>' in open(out_file).read()
    finally:
        os.remove(out_file)


def test_main_with_base_url_file(monkeypatch):
    out_file = os.path.join(BASE_PATH, 'test_report.html')
    monkeypatch.setattr(sys, "argv", ['app.py', os.path.join(BASE_PATH, 'report_example.json'),
                                      '--path', os.path.join(BASE_PATH, '..', 'templates'),
                                      '--base', '/localhost/',
                                      '--output', out_file])
    bandit_tools.custom_report.main()

    try:
        assert '<base href = "file:///localhost/"/>' in open(out_file).read()
    finally:
        os.remove(out_file)
