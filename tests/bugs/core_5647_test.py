#coding:utf-8
#
# id:           bugs.core_5647
# title:        Increase number of formats/versions of views from 255 to 32K
# decription:
#                  FB40SS, build 4.0.0.789: OK, 3.828s (SS, CS).
#                  Older version issued:
#                       Statement failed, SQLSTATE = 54000
#                       unsuccessful metadata update
#                       -TABLE VW1
#                       -too many versions
#                  NB: we have to change FW to OFF in order to increase speed of this test run thus use test_type = Python.
#
#                  05.05.2021.
#                  Reduced min_version to 3.0.8 after this feature was backported to FB 3.x, see:
#                  https://github.com/FirebirdSQL/firebird/commit/14eac8b76bb4d2fb339e5387dd86927961e77d46
#
#                  Re-implemented in order to generate SQL script with more than 2K changes of view format
#                  (see 'FORMAT_CHANGES_LIMIT': this value must be multiplied for 2 in order to get actual number of format changes)
#
#                  Checked on intermediate build 3.0.8.33465, timestamp: 05.05.2021 11:26.
#                  Duration: 4.0.0.2465 ~17s; 3.0.8.33465: ~24s
#                  21.05.2021: changed connection protocol to local, time reduced from 19 to 15 seconds.
#
# tracker_id:   CORE-5647
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#  runProgram('gfix',[dsn,'-w','async'])
#
#  script='''
#      set bail on;
#      set list on;
#      set term ^;
#      execute block returns(ret_code smallint) as
#          declare n int = 300;
#      begin
#          while (n > 0) do
#            begin
#              if (mod(n, 2) = 0) then
#                begin
#                  in autonomous transaction do
#                    begin
#                      execute statement 'create or alter view vw1 (dump1) as select 1 from rdb$database';
#                    end
#                end
#              else
#                begin
#                  in autonomous transaction do
#                    begin
#                      execute statement 'create or alter view vw1 (dump1, dump2) as select 1, 2 from rdb$database';
#                    end
#                end
#              n = n - 1;
#            end
#            ret_code = -abs(n);
#            suspend;
#      end ^
#      set term ;^
#      quit;
#  '''
#  runProgram('isql',[dsn],script)
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    RET_CODE                        0
"""

test_script_1 = """
    set bail on;
    set list on;
    set term ^;
    execute block returns(ret_code smallint) as
        declare n int = 300;
    begin
        while (n > 0) do
          begin
            if (mod(n, 2) = 0) then
              begin
                in autonomous transaction do
                  begin
                    execute statement 'create or alter view vw1 (dump1) as select 1 from rdb$database';
                  end
              end
            else
              begin
                in autonomous transaction do
                  begin
                    execute statement 'create or alter view vw1 (dump1, dump2) as select 1, 2 from rdb$database';
                  end
              end
            n = n - 1;
          end
          ret_code = -abs(n);
          suspend;
    end ^
    set term ;^
    quit;
"""

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=[], input=test_script_1)
    assert act_1.clean_stdout == act_1.clean_expected_stdout
