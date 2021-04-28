#coding:utf-8
#
# id:           bugs.core_6083
# title:        USING PLUGIN clause does not work in RECREATE USER
# decription:   
#                   Confirmed bug on WI-T4.0.0.1530, got:
#                   ===
#                       Statement failed, SQLSTATE = 23000
#                       add record error
#                       -violation of PRIMARY or UNIQUE KEY constraint "INTEG_5" on table "PLG$SRP"
#                       -Problematic key value is ("PLG$USER_NAME" = 'TMP$C6083')
#                   ===
#                   Checked on 4.0.0.1532, SS and CS: OK, 2.085s.
#                
# tracker_id:   CORE-6083
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Following code should NOT raise any output: neither in STDOUT nor in STDERR.
    set bail on;
    set term ^;
    execute block as
    begin
       begin
           -- Here we 'silently drop' user if it remained after previous (failed) run of this test.
           -- Exception about non-existent user will be suppressed:
           execute statement( 'drop user tmp$c6083 using plugin Srp' ) with autonomous transaction;
       when any do
           begin
           end
       end
    end
    ^
    set term ;^
    commit;

    recreate user tmp$c6083 password '123' using plugin Srp;
    recreate user tmp$c6083 password '456' using plugin Srp; -- THIS (second) statement raised error before ticket was fixed.
    commit;

    connect '$(DSN)' user tmp$c6083 password '456'; -- here we want to be sure that user was created SUCCESSFULLY.
    commit;

    connect '$(DSN)' user sysdba password 'masterkey';

    drop user tmp$c6083 using plugin Srp;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.execute()

