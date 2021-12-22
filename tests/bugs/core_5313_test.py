#coding:utf-8
#
# id:           bugs.core_5313
# title:        Data type unknown error with LIST
# decription:
# tracker_id:   CORE-5313
# min_versions: ['3.0.1']
# versions:     3.0.1, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    set sqlda_display on;
    select list(trim(rdb$relation_name), ?) from rdb$relations;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INPUT message field count: 1
    01: sqltype: 452 TEXT scale: 0 subtype: 0 len: 4 charset: 4 UTF8
      :  name:   alias:
      : table:   owner:

    PLAN (RDB$RELATIONS NATURAL)

    OUTPUT message field count: 1
    01: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
      :  name: LIST  alias: LIST
      : table:   owner:
"""

@pytest.mark.version('>=3.0.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute(charset='utf8')
    assert act_1.clean_stdout == act_1.clean_expected_stdout

