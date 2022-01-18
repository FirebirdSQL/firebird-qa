#coding:utf-8

"""
ID:          issue-875
ISSUE:       875
TITLE:       Permissions are checked case-insensitively
DESCRIPTION:
JIRA:        CORE-521
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    create user tmp$c0521 password '123';
    commit;

    set term ^;
    create procedure perm
    as begin
    end^

    create procedure "PeRm"
    as begin
      execute procedure perm;
    end^

    create procedure "pErM"
    as begin
      --execute procedure perm;
      execute procedure "PeRm";
    end^
    set term ;^
    commit;

    grant execute on procedure perm to procedure "PeRm";
    grant execute on procedure "pErM" to user tmp$c0521;
    commit;

    connect '$(DSN)' user tmp$c0521 password '123';
    set list on;
    select current_user as whoami from rdb$database;
    execute procedure "pErM";

    commit;
    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$c0521;
    commit;
"""

act = isql_act('db', test_script, substitutions=[('execute', 'EXECUTE'), ('-Effective user is.*', '')])

expected_stdout = """
    WHOAMI                          TMP$C0521
"""

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    no permission for EXECUTE access to PROCEDURE PeRm
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

