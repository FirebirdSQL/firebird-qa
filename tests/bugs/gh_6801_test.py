#coding:utf-8
#
# id:           bugs.gh_6801
# title:        FB crashes on attempt to recompile a package with some combination of nested functions
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6801
#               
#                   Confirmed crash on 4.0.0.2506; 5.0.0.60
#                   Checked on 5.0.0.63 SS/CS, 4.0.0.2508 (intermediate build, 08-jun-2021 19:28) - all OK.
#                
# tracker_id:   
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
    set bail on;
    set heading off;
    select 'run-1' as msg from rdb$database;

    set term ^ ;
    create or alter package pkg_test as
    begin
      function get_usr_name()
       returns varchar(30);

      function get_usr_id()
       returns bigint;

      procedure create_usr(p_user_name varchar(30))
        returns (p_id bigint);

    end
    ^

    recreate package body pkg_test as
    begin
      function get_usr_name()
       returns varchar(30)
      as
      begin
        return 'TEST_USER';
      end

      function get_usr_id()
       returns bigint
      as
        declare variable v_sess_usr_name varchar(30);
      begin
        v_sess_usr_name = get_usr_name();
        return 123;

      end

      procedure create_usr(p_user_name varchar(30))
        returns (p_id bigint)
      as
        declare variable v_sess_usr_id bigint;
      begin
        v_sess_usr_id = pkg_test.get_usr_id();
      end

    end
    ^

    select 'run-2' as msg from rdb$database
    ^

    create or alter package pkg_test as
    begin
      function get_usr_name()
       returns varchar(30);

      function get_usr_id()
       returns bigint;

      procedure create_usr(p_user_name varchar(30))
        returns (p_id bigint);

    end^

    recreate package body pkg_test as
    begin
      function get_usr_name()
       returns varchar(30)
      as
      begin
        return 'TEST_USER';
      end

      function get_usr_id()
       returns bigint
      as
        declare variable v_sess_usr_name varchar(30);
      begin
        -- No crash in both cases: with or without package name:
        v_sess_usr_name = get_usr_name();
        return 123;
      end

      procedure create_usr(p_user_name varchar(30))
        returns (p_id bigint)
      as
        declare variable v_sess_usr_id bigint;
      begin
        -- This call led FB to crash, regardless on specifiyng prefix of package ('pkg_test'):
        v_sess_usr_id = pkg_test.get_usr_id();
        -- v_sess_usr_id = get_usr_id();
      end

    end
    ^
    select 'completed' as msg from rdb$database
    ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    run-1
    run-2
    completed
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
