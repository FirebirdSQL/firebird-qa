#coding:utf-8
#
# id:           bugs.core_5747
# title:        User can grant usage privilege by himself
# decription:   
#                   Confirmed bug on: 4.0.0.890; 3.0.4.32912
#                   Works fine on:
#                       3.0.4.32917: OK, 1.891s.
#                       4.0.0.907: OK, 1.765s.
#                   Note: beside generator we also have to check the same issue about grant usage on exception.
#                
# tracker_id:   CORE-5747
# min_versions: ['3.0.4']
# versions:     3.0.4, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = [('no G privilege with grant option on object .*', 'no USAGE privilege with grant option on object'), ('GEN_FOR_DBA_ONLY', ''), ('EXC_FOR_DBA_ONLY', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    commit;
    connect '$(DSN)' user sysdba password 'masterkey';

    create or alter user tmp$c5747 password '123';
    commit;

    recreate sequence gen_for_dba_only;
    recreate exception exc_for_dba_only 'Your names is: @1 - and you should not be able to use this exception!';
    commit;

    connect '$(DSN)' user tmp$c5747 password '123';

    grant usage on generator gen_for_dba_only to tmp$c5747;
    grant usage on exception exc_for_dba_only to tmp$c5747;
    commit;

    connect '$(DSN)' user tmp$c5747 password '123';

    set list on;
    
    select gen_id(gen_for_dba_only,1) as next_secret_system_sequence from rdb$database;
    set term ^;
    execute block as
    begin
        exception exc_for_dba_only using (current_user);
    end
    ^
    set term ;^

    commit;
    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$c5747;
    commit;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -no USAGE privilege with grant option on object
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -no USAGE privilege with grant option on object
    Statement failed, SQLSTATE = 28000
    no permission for USAGE access to GENERATOR
    Statement failed, SQLSTATE = 28000
    no permission for USAGE access to EXCEPTION
"""

@pytest.mark.version('>=3.0.4,<4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

# version: 4.0
# resources: None

substitutions_2 = [('no G privilege with grant option on object .*', 'no USAGE privilege with grant option on object'), ('GEN_FOR_DBA_ONLY', ''), ('EXC_FOR_DBA_ONLY', '')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    commit;
    connect '$(DSN)' user sysdba password 'masterkey';

    create or alter user tmp$c5747 password '123';
    commit;

    recreate sequence gen_for_dba_only;
    recreate exception exc_for_dba_only 'Your names is: @1 - and you should not be able to use this exception!';
    commit;

    connect '$(DSN)' user tmp$c5747 password '123';

    grant usage on generator gen_for_dba_only to tmp$c5747;
    grant usage on exception exc_for_dba_only to tmp$c5747;
    commit;

    connect '$(DSN)' user tmp$c5747 password '123';

    set list on;
    
    select gen_id(gen_for_dba_only,1) as next_secret_system_sequence from rdb$database;
    set term ^;
    execute block as
    begin
        exception exc_for_dba_only using (current_user);
    end
    ^
    set term ;^

    commit;
    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$c5747;
    commit;

"""

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stderr_2 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -no USAGE privilege with grant option on object

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -no USAGE privilege with grant option on object

    Statement failed, SQLSTATE = 28000
    no permission for USAGE access to GENERATOR
    -Effective user is TMP$C5747

    Statement failed, SQLSTATE = 28000
    no permission for USAGE access to EXCEPTION
    -Effective user is TMP$C5747
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_stderr == act_2.clean_expected_stderr

