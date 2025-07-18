#coding:utf-8

"""
ID:          trigger.database.connect-02
TITLE:       Error handling in trigger on database connect
DESCRIPTION:
  This test verifies the proper error handling: uncaught exceptions
  in trigger ON CONNECT have to roll back changes of transaction,
  disconnect the attachment and are returned to the client.
FBTEST:      functional.trigger.database.connect_02
NOTES:
[26.05.2022] pzotov
  Re-implemented for work in firebird-qa suite. 
  Checked on: 3.0.8.33535, 4.0.1.2692, 5.0.0.497
"""

import pytest
from firebird.qa import *

db = db_factory()
tmp_worker = user_factory('db', name='tmp_worker', password='123')
tmp_hacker = user_factory('db', name='tmp_hacker', password='456')

act = python_act('db', substitutions=[('line:.*', '')])


@pytest.mark.version('>=3.0')
def test_1(act: Action, tmp_worker: User, tmp_hacker: User):

    SQL_SCHEMA_PREFIX = '' if act.is_version('<6') else '"PUBLIC".'
    TEST_EXC_NAME = 'EXC_CONNECT' if act.is_version('<6') else f'{SQL_SCHEMA_PREFIX}"EXC_CONNECT"'
    TEST_TRG_NAME = "'TRG_CONNECT'" if act.is_version('<6') else f'{SQL_SCHEMA_PREFIX}"TRG_CONNECT"'
    expected_stdout = f"""
        Statement failed, SQLSTATE = HY000
        exception 1
        -{TEST_EXC_NAME}
        -Exception in ON CONNECT trigger for {tmp_hacker.name}
        -At trigger {TEST_TRG_NAME}

        ID                              1
        AUDIT_WHO                       {tmp_worker.name}
        ID                              2
        AUDIT_WHO                       {tmp_hacker.name}
        Records affected: 2

        ID                              1
        SESSION_WHO                     {tmp_worker.name}
        Records affected: 1
    """

    script = f"""
        create table sessions_in_work(
            id int generated by default as identity constraint pk_ssn_in_work primary key
            ,session_who varchar(31) default current_user
        );

        create table sessions_audit(
            id int generated by default as identity constraint pk_ssn_audit primary key
            ,audit_who varchar(31) default current_user
        );
        create exception exc_connect 'Exception in ON CONNECT trigger for @1';

        set term ^;
        create trigger trg_connect on connect position 0 as
        begin
          if ( current_user = '{act.db.user}' ) then
              exit;

          in autonomous transaction do
              insert into sessions_audit default values;

          insert into sessions_in_work default values;

          if ( current_user = upper('{tmp_hacker.name}') ) then
              exception exc_connect using(current_user);
        end
        ^
        set term ;^
        commit;
        -----------------------------------------------------
        connect '{act.db.dsn}' user '{tmp_worker.name}' password '{tmp_worker.password}';
        commit;

        connect '{act.db.dsn}' user '{tmp_hacker.name}' password '{tmp_hacker.password}';
        commit;
        -----------------------------------------------------

        -- Connect as DBA for obtaining results:
        connect '{act.db.dsn}' user '{act.db.user}' password '{act.db.password}';
        set list on;
        set count on;
        select * from sessions_audit;
        select * from sessions_in_work;
    """

    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input = script, combine_output=True)
    assert act.clean_stdout == act.clean_expected_stdout
