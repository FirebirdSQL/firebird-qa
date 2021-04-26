#coding:utf-8
#
# id:           bugs.core_3447
# title:        Collation is not installed with icu > 4.2
# decription:   
# tracker_id:   CORE-3447
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(
        name1 varchar(32) character set utf8 collate ucs_basic,
        name2 varchar(32) character set utf8 collate unicode,
        name3 varchar(32) character set utf8 collate unicode_ci,
        name4 varchar(32) character set utf8 collate unicode_ci_ai
    );
    commit;
    show table test;
    -- Passed on: WI-V2.5.5.26871, WI-T3.0.0.31844; LI-V2.5.3.26788, LI-T3.0.0.31842
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    NAME1                           VARCHAR(32) CHARACTER SET UTF8 Nullable
                                     COLLATE UCS_BASIC
    NAME2                           VARCHAR(32) CHARACTER SET UTF8 Nullable
                                     COLLATE UNICODE
    NAME3                           VARCHAR(32) CHARACTER SET UTF8 Nullable
                                     COLLATE UNICODE_CI
    NAME4                           VARCHAR(32) CHARACTER SET UTF8 Nullable
                                     COLLATE UNICODE_CI_AI
  """

@pytest.mark.version('>=2.5.1')
def test_core_3447_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

