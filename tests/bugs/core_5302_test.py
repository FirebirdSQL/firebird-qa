#coding:utf-8
#
# id:           bugs.core_5302
# title:        Performance regression when bulk inserting into table with indices
# decription:
#                   Test uses TWO tables, one w/o indices and another with indexes.
#                   We evaluate RATIO between performance rather than absolute duration values.
#                   This ratio then is compared with THRESHOLD which was choosen after dozen runs
#                   of test on FB 3.0 and 4.0.
#
#                   _BEFORE_ this ticket was fixed ratio was following:
#
#                   Ratio for 4.0.0.258: ~32...34 -- poor
#                   Ratio for 3.0.1.32566: ~23...24 -- poor
#
#                   _AFTER_ ticket was fixed ratio is:
#
#                   Ratio for 4.0.0.313:   ~11...13 -- OK
#                   Ratio for 3.0.1.32568: ~10...11 -- OK
#
#                   Fix for 4.0 was 07-jul-2016, see here:
#                   https://github.com/FirebirdSQL/firebird/commit/a75e0af175ea6e803101b5fd62ec91cdf039b951
#                   Fix for 3.0 was 27-jul-2016, see here:
#                   https://github.com/FirebirdSQL/firebird/commit/96a24228b61003e72c68596faf3c4c4ed0b95ea1
#
#                   All measures were done on regular PC, OS = Windows XP, CPU 3.0 Ghz, RAM 2 Gb, HDD IDE.
#                   05.01.2020: increased threshold from 15 to 20 (Win 2008 Server R2, ram 8gb)
#                   Checked on:
#                       4.0.0.1714  SS: 5.922s; 4.0.0.1714  SC: 7.891s; 4.0.0.1714  CS: 9.891s.
#                       3.0.5.33221 SS: 4.735s; 3.0.5.33221 SC: 5.718s; 3.0.5.33221 CS: 7.126s.
#
#                   13.01.2020: checked again (Win 8.1 Pro, ram 12 gb):
#                       4.0.0.2325 SS: 5.806s.
#                       4.0.0.2324 SC: 5.812s.
#                       4.0.0.2324 CS: 6.651s.
#                       3.0.8.33401 SS: 5.366s.
#                       3.0.8.33401 SC: 4.823s.
#                       3.0.8.33401 CS: 6.089s.
#
#                  [pcisar] 21.10.2021 - This test is sensitive to user test environment, and may FAIL on slow drives/machines !!!
#
# tracker_id:   CORE-5302
# min_versions: ['3.0.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table test0(x int, y int, z int);
    recreate table test1(x int, y int, z int);
    create index test1_x on test1(x);
    create index test1_y on test1(y);
    create index test1_z on test1(z);
    create index test1_xy on test1(x, y);
    create index test1_xz on test1(x, z);
    create index test1_xyz on test1(x, y, z);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set term ^;
    execute block returns(msg varchar(100)) as
      declare n int = 50000;
      declare m int;
      declare t0 timestamp;
      declare t1 timestamp;
      declare t2 timestamp;
      declare max_ratio numeric(12,4) = 20;
      --                                ^
      --                                |
      --                                +--- #####  T H R E S H O L D  #####
      declare cur_ratio numeric(12,4);
    begin
      t0='now';
      m = n;
      while(m>0) do insert into test0(x, y, z) values(:m, :m, :m) returning :m-1 into m;

      t1='now';
      m = n;
      while(m>0) do insert into test1(x, y, z) values(:m, :m, :m) returning :m-1 into m;
      t2='now';

      cur_ratio = 1.0000 * datediff(millisecond from t1 to t2) / datediff(millisecond from t0 to t1);

      msg = iif( cur_ratio < max_ratio,
                 'OK, ratio is acceptable',
                 'POOR: ratio = ' || cur_ratio || ' - exceeds threshold = ' || max_ratio
               );
      suspend;

    end
    ^
    set term ;^
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             OK, ratio is acceptable
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.charset = 'NONE'
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

