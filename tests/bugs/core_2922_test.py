#coding:utf-8
#
# id:           bugs.core_2922
# title:        Character set used in constants is not registered as dependency
# decription:
# tracker_id:   CORE-2922
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1, charset='utf8')

test_script_1 = """
    set term ^;
    create or alter procedure p1 as
    declare variable a varchar(10) character set win1250;
    begin
      rdb$set_context('user_session', 'x', :a);
    end
    ^
    create or alter procedure p2 as
    begin
      post_event _win1250'abc';
    end
    ^
    set term ;^
    commit;

    -- show proc;
    set width dep_name 10;
    set width dep_on 10;
    set width dep_on_type 20;
    set list on;

    select rd.rdb$dependent_name dep_name, rd.rdb$depended_on_name dep_on,rt.rdb$type_name dep_on_type
    from rdb$dependencies rd
    join rdb$types rt on
        rd.rdb$depended_on_type = rt.rdb$type
        and rt.rdb$type_name containing upper('COLLATION')
    order by 1;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
DEP_NAME                        P1
DEP_ON                          WIN1250
DEP_ON_TYPE                     COLLATION

DEP_NAME                        P1
DEP_ON                          UTF8
DEP_ON_TYPE                     COLLATION

DEP_NAME                        P2
DEP_ON                          WIN1250
DEP_ON_TYPE                     COLLATION
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

