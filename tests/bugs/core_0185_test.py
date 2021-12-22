#coding:utf-8
#
# id:           bugs.core_0185
# title:        DB crashes if trigger BU deletes own row
# decription:   
#                   Ortiginal test:
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_28.script
#                
# tracker_id:   CORE-0185
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
    create table test (id integer not null);
    commit;
    set term ^ ;
    create trigger test_bu for test active before update position 0 as
    begin
        delete from test where id=old.id;
    end 
    ^
    set term ; ^
    commit;

    insert into test values (1);
    insert into test values (2);
    insert into test values (3);
    insert into test values (4);
    insert into test values (5);
    insert into test values (6);
    commit;

    update test set id=-1 where id=1;
    rollback;
    set list on;
    select count(*) from test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    COUNT                           6
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22000
    no current record for fetch operation
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

