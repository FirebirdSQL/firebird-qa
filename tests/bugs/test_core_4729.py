#coding:utf-8
#
# id:           bugs.core_4729
# title:        Add a flag to mon$database helping to decide what type of security database is used - default, self or other
# decription:   
# tracker_id:   CORE-4729
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
    set wng off;
    set list on;

    create or alter user ozzy password 'osb';
    revoke all on all from ozzy;
    commit;

    -- Check that info can be seen by SYSDBA:
    select current_user,mon$sec_database from mon$database;
    commit;

    -- Check that info can be seen by non-privileged user:
    connect '$(DSN)' user ozzy password 'osb';
    select current_user,mon$sec_database from mon$database;
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user ozzy;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    USER                            SYSDBA
    MON$SEC_DATABASE                Default
    USER                            OZZY
    MON$SEC_DATABASE                Default
  """

@pytest.mark.version('>=3.0')
def test_core_4729_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

