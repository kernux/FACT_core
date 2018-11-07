import pytest

from ..internal.shell_linter import ShellLinter

MOCK_RESPONSE = '''[
    {
        "file": "src/install/pre_install.sh",
        "line": 8,
        "endLine": 8,
        "column": 30,
        "endColumn": 30,
        "level": "warning",
        "code": 2166,
        "message": "Prefer [ p ] || [ q ] as [ p -o q ] is not well defined."
    },
    {
        "file": "src/install/pre_install.sh",
        "line": 12,
        "endLine": 12,
        "column": 47,
        "endColumn": 47,
        "level": "warning",
        "code": 2046,
        "message": "Quote this to prevent word splitting."
    },
    {
        "file": "src/install/pre_install.sh",
        "line": 44,
        "endLine": 44,
        "column": 25,
        "endColumn": 25,
        "level": "info",
        "code": 2086,
        "message": "Double quote to prevent globbing and word splitting."
    }
]'''

BAD_RESPONSE = '''any/path: any/path: openBinaryFile: does not exist (No such file or directory)
[]
'''


@pytest.fixture(scope='function')
def stub_linter():
    return ShellLinter()


def test_do_analysis(stub_linter, monkeypatch):
    monkeypatch.setattr('plugins.analysis.linter.internal.shell_linter.execute_shell_command_get_return_code', lambda command: (MOCK_RESPONSE, 0))
    result = stub_linter.do_analysis('any/path')

    assert 'full' in result
    assert len(result['full']) == 2, 'info issue should be discarded'

    issue = result['full'][0]

    assert len(issue.keys()) == 5
    assert issue['type'] == 'warning'


def test_do_analysis_bad_invokation(stub_linter, monkeypatch):
    monkeypatch.setattr('plugins.analysis.linter.internal.shell_linter.execute_shell_command_get_return_code', lambda command: (BAD_RESPONSE, 1))
    result = stub_linter.do_analysis('any/path')
    assert 'full' not in result


def test_do_analysis_bad_status_code(stub_linter, monkeypatch):
    monkeypatch.setattr('plugins.analysis.linter.internal.shell_linter.execute_shell_command_get_return_code', lambda command: (MOCK_RESPONSE, 2))
    result = stub_linter.do_analysis('any/path')
    assert 'full' not in result
