#coding:utf-8
#
# id:           bugs.core_3808
# title:        Provide ability to return all columns using RETURNING (eg RETURNING *)
# decription:   
#                   Ability to use 'returning *' is verified both in DSL and PSQL.
#                   Checked on: 4.0.0.1455: OK, 1.337s.
#               
#                   30.10.2019. NB: new datatype in FB 4.0 was introduces: numeric(38,0).
#                   It can lead to additional ident of values when we show them in form "SET LIST ON",
#                   so we have to ignore all internal spaces - see added 'substitution' section below.
#                
# tracker_id:   CORE-3808
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    recreate table test(id int default 2, x computed by ( id*2 ), y computed by ( x*x ), z computed by ( y*y ) );
    commit;
    
    insert into test default values returning *;

    update test set id=3 where id=2 returning *;
    
    set term ^;
    execute block returns( deleted_id int, deleted_x bigint, deleted_y bigint, deleted_z bigint ) as
    begin
        delete from test where id=3 returning * into deleted_id, deleted_x, deleted_y, deleted_z;
        suspend;
    end
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              2
    X                               4
    Y                               16
    Z                               256

    ID                              3
    X                               6
    Y                               36
    Z                               1296

    DELETED_ID                      3
    DELETED_X                       6
    DELETED_Y                       36
    DELETED_Z                       1296
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

