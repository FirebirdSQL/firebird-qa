#coding:utf-8
#
# id:           bugs.core_4561
# title:        BUGCHECK(183) when use cursor with "order by ID+0" and "for update with lock"
# decription:   
# tracker_id:   CORE-4561
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    --  Confirmed on WI-T3.0.0.31852 (CS/SC/SS):
    --  Statement failed, SQLSTATE = XX000
    --  internal Firebird consistency check (wrong record length (183), file: vio.cpp line: 1310)
    --  Statement failed, SQLSTATE = XX000
    --  internal Firebird consistency check (can't continue after bugcheck)
    --  . . .
    recreate table tm(id int);
    commit;
    insert into tm(id) values(1);
    insert into tm(id) values(2); -- at least TWO records need to be added
    commit;
    
    set list on;
    set term ^;
    execute block returns(deleted_count int) as
    begin
      deleted_count = 0;
      for
        select id
        from tm
        order by id+0 -- "+0" is mandatory for getting BCA
        for update with lock -- and this also is mandatory
        as cursor c
      do begin
        delete from tm where current of c;
        deleted_count = deleted_count + 1;
      end
      suspend;
    end^
    set term ;^
    
    set count on;
    set echo on;
    select * from tm;
    rollback;
    select * from tm;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DELETED_COUNT                   2
    select * from tm;
    Records affected: 0
    rollback;
    select * from tm;
    ID                              1
    ID                              2
    Records affected: 2
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

