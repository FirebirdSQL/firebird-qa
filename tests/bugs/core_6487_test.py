#coding:utf-8
#
# id:           bugs.core_6487
# title:        FETCH ABSOLUTE and RELATIVE beyond bounds of cursor should always position immediately before-first or after-last
# decription:   
#                 Confirmed bug on 4.0.0.2365, 3.0.8.33415.
#                 Checked on 4.0.0.2369, 3.0.8.33416 - works OK.
# tracker_id:   CORE-6487
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = [('-At block line:.*', '-At block line')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;
    set term ^;
    execute block returns(id int, rc int) as
        declare c scroll cursor for
        (
            select  1 id from rdb$database union all
            select  2 id from rdb$database union all
            select  3 id from rdb$database
        )
        ;
    begin
        open c;
        fetch absolute 9223372036854775807 from c;

        fetch relative -(9223372036854775807-2) from c;
        id = c.id;
        rc = row_count;
        suspend;
        
        close c;
    end
    ^

    execute block returns(id int, rc int) as
        declare c scroll cursor for
        (
            select  1 id from rdb$database union all
            select  2 id from rdb$database union all
            select  3 id from rdb$database
        )
        ;
    begin
        open c;
        fetch absolute -9223372036854775808 from c;

        fetch relative (9223372036854775806) from c;
        id = c.id;
        rc = row_count;
        suspend;
        
        close c;
    end
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY109
    Cursor C is not positioned in a valid record
    -At block line: 14, col: 5

    Statement failed, SQLSTATE = HY109
    Cursor C is not positioned in a valid record
    -At block line: 14, col: 5
  """

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

