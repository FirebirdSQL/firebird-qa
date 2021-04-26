#coding:utf-8
#
# id:           bugs.core_4457
# title:        DATEADD should support fractional value for MILLISECOND
# decription:   
# tracker_id:   CORE-4457
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
    select cast(dateadd(-1 * extract(millisecond from ts) millisecond to ts) as varchar(30)) dts, extract(millisecond from ts) ms
    from (
        select timestamp'2014-06-09 13:50:17.4971' as ts
        from rdb$database
    ) a;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DTS                             2014-06-09 13:50:17.0000
    MS                              497.1
  """

@pytest.mark.version('>=3.0')
def test_core_4457_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

