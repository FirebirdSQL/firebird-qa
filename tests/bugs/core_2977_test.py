#coding:utf-8
#
# id:           bugs.core_2977
# title:        FB 2.1 incorrectly works with indexed fields of type DATE in OLD ODS (9.1)
# decription:
#                  08.04.2021: number of DAY in the date representation becomes padded with '0' (NB: dialect 1 is used here!)
#                  Expected output was changed according to this after discuss with Adriano.
#
# tracker_id:   CORE-2977
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('01-JAN-', ' 1-JAN-')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=1, init=init_script_1)

test_script_1 = """
    recreate table test(id int, opdate timestamp);
    insert into test values(1, '31.12.2000');
    insert into test values(2, '01.01.2001');
    insert into test values(3, '02.01.2001');
    insert into test values(4, '03.01.2001');
    commit;

    create index test_opdate on test(opdate);
    commit;

    set list on;
    -- Following query will have PLAN (TEST INDEX (TEST_OPDATE))
    select * from test where opdate <= '1/1/2001';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    OPDATE                          31-DEC-2000
    ID                              2
    OPDATE                           1-JAN-2001
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

