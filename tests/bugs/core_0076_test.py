#coding:utf-8
#
# id:           bugs.core_0076
# title:        Invalid ROW_COUNT variable value after DELETE
# decription:
# tracker_id:   CORE-0076
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter procedure test_del as begin end;

    recreate table test (
        a integer not null,
        constraint test_pk primary key (a)
    );
    insert into test (a) values (1);
    insert into test (a) values (2);
    insert into test (a) values (3);
    insert into test (a) values (4);
    insert into test (a) values (5);
    insert into test (a) values (6);
    insert into test (a) values (7);
    insert into test (a) values (8);
    insert into test (a) values (9);
    insert into test (a) values (10);
    commit;

    set list on;
    select count(*) as cnt from test where a between 4 and 7;

    set term ^;
    create or alter procedure test_del (l integer, r integer) returns (rc integer) as
    begin
        delete from test where a between :l and :r;
        rc = row_count;
        suspend;
    end
    ^
    set term ;^
    execute procedure test_del (4, 7);
    select * from test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CNT                             4
    RC                              4
    A                               1
    A                               2
    A                               3
    A                               8
    A                               9
    A                               10
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

