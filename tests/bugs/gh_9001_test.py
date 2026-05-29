#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9001
TITLE:       Restart value of Identity field failed on Firebird 6.0, no problem on previous version
DESCRIPTION:
NOTES:
    [29.05.2026]
    Confirmed bug on 6.0.0.1948-8124134.
    Checked on 6.0.0.1948-3fadfab.
"""

import pytest
from firebird.qa import *

db = db_factory(charset='UTF8')

test_script = """
    set bail on;
    set list on;
    create table test1(id int generated always as identity primary key using index test1_id_pk, x int);
    alter table test1 alter id restart with 101;
    commit;
    insert into test1(x) values(1) returning id as generated_id;
"""

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    GENERATED_ID 101
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
