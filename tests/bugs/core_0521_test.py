#coding:utf-8
#
# id:           bugs.core_0521
# title:        Permissions are checked case-insensitively
# decription:   
#                
# tracker_id:   CORE-521
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('execute', 'EXECUTE'), ('-Effective user is.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHOAMI                          TMP$C0521
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    no permission for EXECUTE access to PROCEDURE PeRm
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

