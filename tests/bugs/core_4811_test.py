#coding:utf-8
#
# id:           bugs.core_4811
# title:        Make user names behave according to SQL identifiers rules
# decription:   
# tracker_id:   CORE-4811
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('set echo.*', ''), ('Use CONNECT or CREATE DATABASE.*', ''), ('Your user name and password.*', ''), ('line: [0-9]+, col: [0-9]+', ''), ('exception [0-9]+', 'exception')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    set list on;
    create or alter procedure sp_check_actual_role as begin end;
    set term ^;
    execute block as
    begin
        execute statement 'drop role Boss';
        when any do begin end
    end ^
    set term ;^
    commit;

    recreate exception ex_have_no_role 'You''ve specified role: >@1< -- but your actual role is NONE.';

    set term ^;
    create or alter procedure sp_check_actual_role(
        a_probe_role varchar(31)
    ) returns(
        checking varchar(80),
        result varchar(31)
    ) as
    begin
        if ( upper(current_role) = 'NONE' )
        then
            exception ex_have_no_role using ( a_probe_role );

        checking = 'role: >' || a_probe_role || '< - '
                   || trim(
                           iif( a_probe_role containing '''', 'in apostrophes',
                               iif( a_probe_role containing '"', 'in double quotes', 'without delimiters' )
                              )
                          )
                   || ', ' || iif( upper(a_probe_role) = a_probe_role, 'UPPER case', 'CaMeL case' )
        ;
        result = current_role;
        suspend;
    end
    ^
    set term ;^
    commit;

    set bail on;
    set echo on;
    create or alter user Tmp$c4811 password '1';
    revoke all on all from Tmp$c4811;
    create role Boss;
    grant Boss to Tmp$c4811;
    grant usage on exception ex_have_no_role to Tmp$c4811;
    grant execute on procedure sp_check_actual_role to Tmp$c4811;
    set echo off;
    set bail off;
    -- show grants;
    commit;

    -- set echo on;

    -- checking for USER name:

    connect '$(DSN)' user 'Tmp$c4811' password '1';
    -- PASSES since http://sourceforge.net/p/firebird/code/62016 (2015-07-16 14:26), this was build = 31981
    select 'user: >''Tmp$c4811''< - in apostrophes, CaMeL case' checking, current_user as result from rdb$database;
    commit;

    connect '$(DSN)' user 'TMP$C4811' password '1'; -- should PASS, checked on builds 31948, 31981
    select 'user: >''TMP$C4811''< - in apostrophes, UPPER case' checking, current_user as result from rdb$database;
    commit;

    connect '$(DSN)' user Tmp$c4811 password '1'; -- should PASS, checked on builds 31948, 31981
    select 'user: >Tmp$c4811< - without delimiters, CaMeL case' checking, current_user as result from rdb$database;
    commit;

    connect '$(DSN)' user TMP$C4811 password '1'; -- should PASS, checked on builds 31948, 31981
    select 'user: >TMP$C4811< - without delimiters, UPPER case' checking, current_user as result from rdb$database;
    commit;

    connect '$(DSN)' user "Tmp$c4811" password '1'; -- should *** FAIL ***
    select 'user: >"Tmp$c4811"< - in double quotes, CaMeL case' checking, current_user as result from rdb$database;
    commit;

    connect '$(DSN)' user "TMP$C4811" password '1'; -- should PASS, checked on builds 31948, 31981
    select 'user: >"TMP$C4811" - in double quotes, UPPER case' checking, current_user as result from rdb$database;
    commit;

    -- checking for ROLE (actual role in all following cases will be: [BOSS], checked on builds 31948, 31981)

    -- Statement that created role (see above):
    -- create role Boss;

    -- Enclosing role in apostrophes and specifying it exactly like it was in its creation sttm:
    connect '$(DSN)' user 'TMP$C4811' password '1' role 'Boss';
    select * from sp_check_actual_role( '''Boss''' ); --------------- should return: BOSS
    commit;

    -- Enclosing role in apostrophes and specifying it in UPPERCASE (i.e. differ than in its CREATE ROLE statement):
    connect '$(DSN)' user 'TMP$C4811' password '1' role 'BOSS';
    select * from sp_check_actual_role( '''BOSS''' ); --------------- should return: BOSS
    commit;

    -- do NOT enclosing role in any delimiters and change CaSe of its characters (i.e. differ than in its CREATE ROLE statement):
    connect '$(DSN)' user 'TMP$C4811' password '1' role BosS;
    select * from sp_check_actual_role( 'BosS' );     --------------- should return: BOSS
    commit;

    -- do NOT enclosing role in any delimiters and specifying it in UPPERCASE (i.e. differ than in its CREATE ROLE statement):
    connect '$(DSN)' user 'TMP$C4811' password '1' role BOSS;
    select * from sp_check_actual_role( 'BOSS' );      --------------- should return: BOSS
    commit;

    -- Enclosing role in double quotes and change CaSe of its characters (i.e. differ than in its CREATE ROLE statement):
    connect '$(DSN)' user 'TMP$C4811' password '1' role "BoSs";
    select * from sp_check_actual_role( '"BoSs"' );    --------------- should raise EX_HAVE_NO_ROLE, actual role will be 'NONE'
    commit;

    -- Enclosing role in double quotes and specifying it in UPPERCASE (i.e. differ than in its CREATE ROLE statement):
    connect '$(DSN)' user 'TMP$C4811' password '1' role "BOSS";
    select * from sp_check_actual_role( '"BOSS"' );    --------------- should return: BOSS
    commit;

    -- ### CLEANUP ###
    -- Do not forget about cleanup (other tests can query sec$users or run `show users`!)
    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop user Tmp$c4811;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    create or alter user Tmp$c4811 password '1';
    revoke all on all from Tmp$c4811;
    create role Boss;
    grant Boss to Tmp$c4811;
    grant usage on exception ex_have_no_role to Tmp$c4811;
    grant execute on procedure sp_check_actual_role to Tmp$c4811;

    CHECKING                        user: >'Tmp$c4811'< - in apostrophes, CaMeL case
    RESULT                          TMP$C4811

    CHECKING                        user: >'TMP$C4811'< - in apostrophes, UPPER case
    RESULT                          TMP$C4811

    CHECKING                        user: >Tmp$c4811< - without delimiters, CaMeL case
    RESULT                          TMP$C4811

    CHECKING                        user: >TMP$C4811< - without delimiters, UPPER case
    RESULT                          TMP$C4811

    CHECKING                        user: >"TMP$C4811" - in double quotes, UPPER case
    RESULT                          TMP$C4811

    CHECKING                        role: >'Boss'< - in apostrophes, CaMeL case
    RESULT                          BOSS

    CHECKING                        role: >'BOSS'< - in apostrophes, UPPER case
    RESULT                          BOSS

    CHECKING                        role: >BosS< - without delimiters, CaMeL case
    RESULT                          BOSS

    CHECKING                        role: >BOSS< - without delimiters, UPPER case
    RESULT                          BOSS

    CHECKING                        role: >"BOSS"< - in double quotes, UPPER case
    RESULT                          BOSS
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    Statement failed, SQLSTATE = HY000
    exception 3
    -EX_HAVE_NO_ROLE
    -You've specified role: >"BoSs"< -- but your actual role is NONE.
    -At procedure 'SP_CHECK_ACTUAL_ROLE'
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

