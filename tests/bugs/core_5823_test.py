#coding:utf-8
#
# id:           bugs.core_5823
# title:        No permission for SELECT access to blob field in stored procedure
# decription:   
#                   Confirmed bug on 3.0.4.33034
#                   Checked on: 3.0.4.33053, 4.0.0.1249: OK
#                
# tracker_id:   CORE-5823
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = [('BLOB_FIELD_ID.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter user tmp$c5823 password '123';
    commit;
    set term ^;
    execute block as
    begin
        execute statement 'drop role blob_viewer';
        when any do begin end
    end
    ^
    set term ;^
    commit;
    create role blob_viewer;

    create or alter procedure test_proc (id integer) as begin end;
    commit;

    recreate table test (
        id integer,
        blb blob
    );
    commit;

    insert into test (id, blb) values (1, 'blob1');
    commit;

    set term ^;
    create or alter procedure test_proc (id integer) returns (blb blob) as
    begin
        for 
            select blb from test where id = :id
        into blb
            do suspend;
    end
    ^
    set term ;^
    commit;

    grant select on test to procedure test_proc;
    grant execute on procedure test_proc to blob_viewer;
    grant blob_viewer to tmp$c5823;
    commit;

    connect '$(DSN)' user 'tmp$c5823' password '123' role 'blob_viewer';

    set list on;
    set blob on;
    select mon$user, mon$role from mon$attachments where mon$attachment_id = current_connection;

    select blb as blob_field_id from test_proc(1);
    commit;

    -- cleanup:
    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user tmp$c5823;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """

    MON$USER                        TMP$C5823
    MON$ROLE                        BLOB_VIEWER
    BLOB_FIELD_ID                   80:0
    blob1
  """

@pytest.mark.version('>=3.0.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

