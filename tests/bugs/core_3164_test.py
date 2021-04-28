#coding:utf-8
#
# id:           bugs.core_3164
# title:        Parameterized requests involving blob fields fails when connected using charset UTF8
# decription:   
# tracker_id:   CORE-3164
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table test(fb blob);
    commit;
    insert into test values(rpad('', 7, 'foo') );
    insert into test values(rpad('', 8, 'bar') );
    commit;

    set list on;

    set term ^;
    execute block returns(n int) as
      declare v_blob blob;
    begin

      for
          select fb from test
          into v_blob
      do
          begin
            execute statement ('select octet_length(fb) from test where fb starting with ?') (:v_blob) into n;
            suspend;
          end
    end
    ^
    set term ;^
    -- Confirmed for 2.5.0 (WI-V2.5.0.26074):
    -- Statement failed, SQLSTATE = 22001
    -- arithmetic exception, numeric overflow, or string truncation
    -- -string right truncation
    -- (instead of output N = 8 for second record)
    -- Seems to be relatoed to core-3353 // Predicate (blob_field LIKE ?) describes the parameter as VARCHAR(30) rather than as BLOB
    -- because of SQLDA content:
    -- In 2.5.0: sqltype: 449 VARYING   Nullable sqlscale: 0 sqlsubtype: 4 sqllen: 28
    -- In 2.5.1: sqltype: 521 BLOB     Nullable sqlscale: 0 sqlsubtype: 0 sqllen: 8
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    N                               7
    N                               8
  """

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

