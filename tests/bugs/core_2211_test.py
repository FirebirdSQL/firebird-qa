#coding:utf-8
#
# id:           bugs.core_2211
# title:        Offset value for SUBSTRING from BLOB more than 32767 makes exception
# decription:
# tracker_id:   CORE-2211
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('SUBSTRING.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- [pcisar] 20.10.2021
    -- This script reports error:
    -- Statement failed, SQLSTATE = 54000
    -- arithmetic exception, numeric overflow, or string truncation
    -- -Implementation limit exceeded
    -- -At block line: 7, col: 9
    -- Statement failed, SQLSTATE = 22011
    -- Invalid offset parameter -1 to SUBSTRING. Only positive integers are allowed.

    recreate table test(b blob);
    commit;
    insert into test values('');
    commit;

    set list on;
    set blob all;

    set term ^;
    execute block as
      declare bsize int = 1000000;
      declare vclen int = 32760;
    begin
      while (bsize > 0) do
      begin
        update test set b  = b || rpad('', :vclen, uuid_to_char(gen_uuid()));
        bsize = bsize - vclen;
      end
      --update test set b = b || b;
      update test set b = b || rpad('', :vclen, '#');
    end
    ^
    set term ;^
    select char_length(b) from test;
    select substring(b from char_length(b)-1 for 1) from test;
    rollback;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CHAR_LENGTH                     1048320
    SUBSTRING                       0:43
    #
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.db.set_async_write()
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

