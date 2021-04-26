#coding:utf-8
#
# id:           bugs.core_4839
# title:        SHOW GRANTS does not display info about exceptions which were granted to user
# decription:   
# tracker_id:   CORE-4839
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter user tmp$c4839 password '123';
    recreate exception exc_foo 'Houston we have a problem: next sequence value is @1';
    recreate sequence gen_bar start with 9223372036854775807 increment by 2147483647;
    commit;

    grant usage on exception exc_foo to tmp$c4839; -- this wasn`t shown before rev. 61822 (build 3.0.0.31881), 2015-06-14 11:35
    grant usage on sequence gen_bar to tmp$c4839;
    commit; 
    show grants;
    commit;
    drop user tmp$c4839;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    /* Grant permissions for this database */
    GRANT USAGE ON SEQUENCE GEN_BAR TO USER TMP$C4839
    GRANT USAGE ON EXCEPTION EXC_FOO TO USER TMP$C4839
  """

@pytest.mark.version('>=3.0')
def test_core_4839_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

