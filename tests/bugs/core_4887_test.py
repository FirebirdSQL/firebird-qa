#coding:utf-8
#
# id:           bugs.core_4887
# title:        AFTER CREATE/ALTER PACKAGE DDL triggers runs in incorrectly moment
# decription:   Since WI-V3.0.0.31981 this code should produce only STDOUT and no STDERR.
# tracker_id:   CORE-4887
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
    set bail on;
    set list on;
    create exception exc_empty_pkg 'Empty package';
    create sequence g;
    commit;

    set term ^;
    create or alter trigger t_trig_pkg_head after create package as
    begin
      rdb$set_context('USER_SESSION','DDL_TRIGGER_ON_PKG_HEAD_FIRING', gen_id(g,1));
      if ( not exists(select * from rdb$functions where rdb$package_name = rdb$get_context('DDL_TRIGGER', 'OBJECT_NAME') ) ) then
          exception exc_empty_pkg;
    end
    ^
    create or alter trigger t_trig_pkg_body after create package body as
    begin
      rdb$set_context('USER_SESSION','DDL_TRIGGER_ON_PKG_BODY_FIRING', gen_id(g,1));
    end
    ^    
    set term ;^
    commit;

    set term ^;
    execute block as
    begin
      rdb$set_context('USER_SESSION','PACKAGE_HEADER_CREATION_START',  gen_id(g,1));
    end
    ^
    create package xpk1 as
    begin
      function f1 returns integer;
    end
    ^
    execute block as
    begin
      rdb$set_context('USER_SESSION','PACKAGE_HEADER_CREATION_FINISH',  gen_id(g,1));
    end
    ^
    commit
    ^

    execute block as
    begin
      rdb$set_context('USER_SESSION','PACKAGE_BODY_CREATION_START',  gen_id(g,1));
    end
    ^
    create package body xpk1 as
    begin
      function f1 returns integer as
      begin
         return 12345;
      end
    end
    ^    
    execute block as
    begin
      rdb$set_context('USER_SESSION','PACKAGE_BODY_CREATION_FINISH',  gen_id(g,1));
    end
    ^
    set term ;^

    select event_seq, event_name
    from(
        select
             cast( rdb$get_context('USER_SESSION','PACKAGE_HEADER_CREATION_START') as int) event_seq
            ,'pkg_header_start' event_name
        from rdb$database
        union all    
        select
             cast( rdb$get_context('USER_SESSION','PACKAGE_HEADER_CREATION_FINISH') as int)
            ,'pkg_header_finish'
        from rdb$database
        union all    
        select
            cast( rdb$get_context('USER_SESSION','PACKAGE_BODY_CREATION_START') as int) 
            ,'pkg_body_start'
        from rdb$database
        union all    
        select
            cast( rdb$get_context('USER_SESSION','PACKAGE_BODY_CREATION_FINISH') as int)
            ,'pkg_body_finish'
        from rdb$database
        union all    
        select
            cast( rdb$get_context('USER_SESSION','DDL_TRIGGER_ON_PKG_HEAD_FIRING') as int) 
            ,'trg_pkg_head_firing'
        from rdb$database
        union all    
        select
            cast( rdb$get_context('USER_SESSION','DDL_TRIGGER_ON_PKG_BODY_FIRING') as int)
            ,'trg_pkg_body_firing'
        from rdb$database
    )    
    order by event_seq;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    EVENT_SEQ                       1
    EVENT_NAME                      pkg_header_start
    
    EVENT_SEQ                       2
    EVENT_NAME                      trg_pkg_head_firing
    
    EVENT_SEQ                       3
    EVENT_NAME                      pkg_header_finish
    
    EVENT_SEQ                       4
    EVENT_NAME                      pkg_body_start
    
    EVENT_SEQ                       5
    EVENT_NAME                      trg_pkg_body_firing
    
    EVENT_SEQ                       6
    EVENT_NAME                      pkg_body_finish
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

