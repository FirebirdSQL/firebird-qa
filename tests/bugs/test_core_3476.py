#coding:utf-8
#
# id:           bugs.core_3476
# title:        LIST function wrongly concatenates binary blobs
# decription:   
# tracker_id:   CORE-3476
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select ascii_val( left(list(f,''),1) ) v1, ascii_val( right(list(f,''),1) ) v2
    from (
        select cast(ascii_char(0xff) as blob sub_type 0) as f
        from rdb$database
        union all
        select cast(ascii_char(0xde) as blob sub_type 0) as f
        from rdb$database
    );
    -- NB: proper result will be only in 3.0, WI-V2.5.4.26853 produces:
    -- V1                              46
    -- V2                              46
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    V1                              255
    V2                              222
  """

@pytest.mark.version('>=3.0')
def test_core_3476_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

