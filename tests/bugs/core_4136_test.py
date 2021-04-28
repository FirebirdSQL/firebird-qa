#coding:utf-8
#
# id:           bugs.core_4136
# title:        Sharp-S character treated incorrectly in UNICODE_CI_AI collation
# decription:   
# tracker_id:   CORE-4136
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select
      case when 'Übergeek' collate unicode_ci_ai like 'ÜB%' collate unicode_ci_ai
        then 'match' else 'MISMATCH' end as test_1,
      case when 'Übergeek' collate unicode_ci_ai like 'üb%' collate unicode_ci_ai
        then 'match' else 'MISMATCH' end as test_2,
      case when 'Fußball' collate unicode_ci_ai like 'fu%' collate unicode_ci_ai
        then 'match' else 'MISMATCH' end as test_3,
      case when 'Fußball' collate unicode_ci_ai like 'fuß%' collate unicode_ci_ai
        then 'match' else 'MISMATCH' end as test_4,
      case when upper ('Fußball') like upper ('fuß%')
        then 'match' else 'MISMATCH' end as test_5
    from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TEST_1                          match
    TEST_2                          match
    TEST_3                          match
    TEST_4                          match
    TEST_5                          match  
  """

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

