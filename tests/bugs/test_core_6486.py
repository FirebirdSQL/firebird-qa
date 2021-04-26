#coding:utf-8
#
# id:           bugs.core_6486
# title:        FETCH RELATIVE has an off by one error for the first row
# decription:   
#                 Confirmed bug on 4.0.0.2365.
#                 Checked on 3.0.8.33423, 4.0.0.2369 - works OK.
# tracker_id:   CORE-6486
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set term ^;
    execute block returns(id_fetch_rel1 int, rc_fetch_rel1 int) as
        declare c scroll cursor for
        (
            select  1 id from rdb$database union all
            select  2 id from rdb$database union all
            select  3 id from rdb$database
        )
        ;
    begin
        open c;
        fetch relative 1 from c; 
        id_fetch_rel1 = c.id;
        rc_fetch_rel1 = row_count;
        suspend;
        close c;
    end
    ^

    execute block returns(id_fetch_next int, rc_fetch_next int) as
        declare c scroll cursor for
        (
            select  1 id from rdb$database union all
            select  2 id from rdb$database union all
            select  3 id from rdb$database
        )
        ;
    begin
        open c;
        fetch next from c; 
        id_fetch_next = c.id;
        rc_fetch_next = row_count;
        suspend;
        close c;
    end
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID_FETCH_REL1                   1
    RC_FETCH_REL1                   1
    ID_FETCH_NEXT                   1
    RC_FETCH_NEXT                   1
  """

@pytest.mark.version('>=3.0.8')
def test_core_6486_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

