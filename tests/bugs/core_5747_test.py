#coding:utf-8

"""
ID:          issue-6010
ISSUE:       6010
TITLE:       User can grant usage privilege by himself
DESCRIPTION:
  beside generator we also have to check the same issue about grant usage on exception.
JIRA:        CORE-5747
"""

import pytest
from firebird.qa import *

substitutions = [('no G privilege with grant option on object .*',
                  'no USAGE privilege with grant option on object'),
                 ('GEN_FOR_DBA_ONLY', ''), ('EXC_FOR_DBA_ONLY', '')]

db = db_factory()

test_script = """
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

act = isql_act('db', test_script, substitutions=substitutions)

# version: 3.0

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
def test_1(act: Action):
    act.expected_stderr = expected_stderr_1
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

# version: 4.0

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
def test_2(act: Action):
    act.expected_stderr = expected_stderr_2
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
