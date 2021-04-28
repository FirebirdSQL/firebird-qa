#coding:utf-8
#
# id:           bugs.core_5074
# title:         Lost the charset ID in selection of array element
# decription:   
#                   Confirmed missed charset in SQLDA output (remained "... charset: 0 NONE" in FB 3.0 and 4.0).
#                   As of FB 2.5 there we can check only one difference: "sqlsubtype: 1" instead of old "sqlsubtype: 0".
#                   Checked on:
#                       build 4.0.0.1524: OK, 1.478s.
#                       build 3.0.5.33139: OK, 0.913s.
#                       build 2.5.9.27139: OK, 0.618s.
#                
# tracker_id:   CORE-5074
# min_versions: ['2.5.9']
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
    recreate table test(
        a char(10)[0:3] character set octets
    );
    set sqlda_display on;
    select a[0] from test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INPUT message field count: 0

    OUTPUT message field count: 1
    01: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 10 charset: 1 OCTETS
      :  name: A  alias: A
      : table: TEST  owner: SYSDBA
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

