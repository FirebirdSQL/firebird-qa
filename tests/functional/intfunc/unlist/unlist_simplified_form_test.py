#coding:utf-8

"""
ID:          issue-8418
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/8878
TITLE:       Short syntax for UNLIST with IN operator
DESCRIPTION:
NOTES:
    [11.03.2025] pzotov
    Checked on 6.0.0.1814
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = f"""
    set list on;
    create domain empno as smallint;
    create table employee (
        emp_no empno not null
    );
    insert into employee values('19');
    insert into employee values('13');
    insert into employee values('11');
    insert into employee values('9');
    insert into employee values('2');
    insert into employee values('5');
    insert into employee values('22');
    insert into employee values('44');
    insert into employee values('77');
    insert into employee values('7');

    set count on;
    select e.emp_no from employee e where e.emp_no in unlist('2,4,5,7,11') order by 1;
"""

act = isql_act('db', test_script, substitutions=[ ('[ \\t]+', ' ') ])

expected_stdout = f"""
    EMP_NO 2
    EMP_NO 5
    EMP_NO 7
    EMP_NO 11
    Records affected: 4
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
