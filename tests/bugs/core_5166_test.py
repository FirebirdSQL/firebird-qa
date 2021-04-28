#coding:utf-8
#
# id:           bugs.core_5166
# title:        Wrong error message with UNIQUE BOOLEAN field
# decription:   
# tracker_id:   CORE-5166
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
    -- Confirmed: result is OK, builds: 3.0.0.32418, WI-T4.0.0.98
    set list on;
    recreate table test1 (
        x boolean,
        constraint test1_x_unq unique (x)
        using index test1_x_unq
    );
    commit;
    insert into test1(x) values (true);
    select * from test1;

    set count on;
    insert into test1(x) values (true);
    commit;
    set count off;

    recreate table test2 (
        u boolean,
        v boolean,
        w boolean,
        constraint test2_uvw_unq unique (u,v,w)
        using index test2_uvw_unq
    );
    commit;

    set count on;
    insert into test2 values( null, null, null);
    insert into test2 values( true, true, true);
    insert into test2 values( true, null, true);
    insert into test2 values( true, null, null);
    insert into test2 values( null, true, null);
    insert into test2 values( null, null, null);
    insert into test2 values( true, true, true);
    update test2 set u=true, v=null, w=true where coalesce(u,v,w) is null rows 1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               <true>
    Records affected: 0
    Records affected: 1
    Records affected: 1
    Records affected: 1
    Records affected: 1
    Records affected: 1
    Records affected: 1
    Records affected: 0
    Records affected: 0
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TEST1_X_UNQ" on table "TEST1"
    -Problematic key value is ("X" = TRUE)

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TEST2_UVW_UNQ" on table "TEST2"
    -Problematic key value is ("U" = TRUE, "V" = TRUE, "W" = TRUE)

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TEST2_UVW_UNQ" on table "TEST2"
    -Problematic key value is ("U" = TRUE, "V" = NULL, "W" = TRUE)
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

