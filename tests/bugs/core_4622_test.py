#coding:utf-8
#
# id:           bugs.core_4622
# title:        Regression: Trigger with UPDATE OR INSERT statement and IIF() not working as expected
# decription:   
# tracker_id:   CORE-4622
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block as
    begin
        execute statement 'drop trigger v_test_bu';
    when any do begin end
    end
    ^
    set term ;^
    commit;
    
    create or alter view v_test as select 1 id from rdb$database;
    commit;
    -------------------------------------------------------------
    recreate table test (
        id integer not null,
        a integer,
        b integer,
        constraint pk_test primary key (id)
    );
    commit;
    insert into test values(1, 100, 200);
    commit;
    
    create or alter view v_test as
    select id, a, b from test;
    commit;
    
    set term ^;
    create or alter trigger v_test_bu for v_test
    active before update position 0
    as
    begin
        -- Confirmed on WI-T3.0.0.31374 Firebird 3.0 Beta 1:
        -- Statement failed, SQLSTATE = HY000
        -- invalid request BLR at offset 51
        -- -undefined variable number
        update or insert into test ( id , a , b)
        values ( iif( mod( new.id,2)=0, -new.id, new.id ), new.a, new.b)
        matching( id );
    end
    ^
    set term ;^
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.execute()

