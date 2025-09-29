#coding:utf-8

"""
ID:          issue-1450
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/1450
TITLE:       LIKE doesn't work for computed values (at least in a view)
DESCRIPTION:
JIRA:        CORE-1033
NOTES:
    [29.09.2025] pzotov
    Refactored: show SQLDA, changed table output to the list, added substitutions.
    Checked on 6.0.0.1280; 5.0.4.1715; 4.0.7.3235; 3.0.14.33826.
"""

import pytest
from firebird.qa import *

init_script = """
    create table test (
      part_id numeric(10,0) not null,
      part_descr varchar(50) not null
    );
    create view v_test (part_id, part_descr) as select part_id, x.part_descr || ' ('||x.part_id||')' from test as x;
    commit;

    insert into test values (1,'xyz');
    insert into test values (2,'xyzxyz');
    insert into test values (3,'xyz012');

    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set list on;
    set sqlda_display on;
    select * from v_test rows 0;
    set sqlda_display off;
    set count on;
    select * from v_test where part_descr like 'xyz (1)' ;
    select * from v_test where part_descr like 'xyz (%)' ;
    select * from v_test where part_descr like 'xyz%' ;
"""

substitutions = [ ('^((?!(SQLSTATE|sqltype|PART_ID|PART_DESCR|Records)).)*$', ''), ('[ \t]+', ' '), ('charset:.*', '') ]

act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 1 len: 8
    : name: PART_ID alias: PART_ID
    02: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 280
    : name: PART_DESCR alias: PART_DESCR

    PART_ID 1
    PART_DESCR xyz (1)
    Records affected: 1
    
    PART_ID 1
    PART_DESCR xyz (1)
    Records affected: 1
    
    PART_ID 1
    PART_DESCR xyz (1)
    PART_ID 2
    PART_DESCR xyzxyz (2)
    PART_ID 3
    PART_DESCR xyz012 (3)
    Records affected: 3
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
