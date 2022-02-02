#coding:utf-8

"""
ID:          issue-5601
ISSUE:       5601
TITLE:       Malformed string error when using cyrilic symbols and x'0d0a' in exception
DESCRIPTION:
JIRA:        CORE-5325
FBTEST:      bugs.core_5325
"""

import pytest
from pathlib import Path
from firebird.qa import *

substitutions = [('exception [\\d]+', 'exception'),
                 ('-At block line(:)?\\s+[\\d]+.*', ''),
                 ('After line(:)?\\s+[\\d]+.*', '')]

db = db_factory()

act = python_act('db', substitutions=substitutions)

test_script = """
    create exception error_test 'йцукенг';
    commit;
    set term ^;
    execute block as
    begin
        exception error_test 'йцу' || _win1251 x'0d0a' || 'кенг';
    end^
    set term ;^
"""

script_file = temp_file('test-script.sql')

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -ERROR_TEST
    -йцу

    кенг
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, script_file: Path):
    script_file.write_text(test_script, encoding='cp1251')
    act.expected_stderr = expected_stderr_1
    act.isql(switches=['-q'], input_file=script_file, charset='WIN1251')
    assert act.clean_stderr == act.clean_expected_stderr


