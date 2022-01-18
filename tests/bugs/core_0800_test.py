#coding:utf-8

"""
ID:          issue-1186
ISSUE:       1186
TITLE:       Easy metadata extract improvements
DESCRIPTION: Domain DDL: move its CHECK clause from 'create' to 'alter' statement.
JIRA:        CORE-800
"""

import pytest
from firebird.qa import *

init_script = """
    set term ^;
    execute block as
    begin
      begin
        execute statement 'drop domain dm_test';
        when any do begin end
      end
      begin
        execute statement 'drop collation name_coll';
        when any do begin end
      end
    end^
    set term ;^
    commit;

    create collation name_coll for utf8 from unicode no pad case insensitive accent insensitive;
    commit;

    create domain dm_test varchar(20)
       character set utf8
       default 'foo'
       not null
       check (value in ('foo', 'rio', 'bar'))
       collate name_coll
       ;
    commit;
"""

db = db_factory(charset='UTF8', init=init_script)

act = python_act('db')

expected_stdout = """
    ALTER DOMAIN DM_TEST ADD CONSTRAINT
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.extract_meta()
    expected = ''.join([x for x in act.clean_stdout.splitlines() if 'ALTER DOMAIN' in x.upper()])
    assert act.clean_expected_stdout == expected


