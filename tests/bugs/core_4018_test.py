#coding:utf-8
#
# id:           bugs.core_4018
# title:        Using system domain in procedures arguments/returns cause the proc to be unchangeable
# decription:   
# tracker_id:   CORE-4018
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set blob all;
    set count on;

    set term ^;
    create procedure sp_test returns(info rdb$source) as
    begin
      info = 'foo';
      suspend;
    end
    ^
    set term ;^
    commit;
       
    select 'point-1' as msg, rdb$parameter_name, rdb$parameter_type, rdb$field_source
    from rdb$procedure_parameters 
    where rdb$procedure_name = upper('sp_test')
    order by rdb$parameter_name, rdb$parameter_type;

    select 'point-2' as msg, rdb$procedure_source 
    from rdb$procedures 
    where rdb$procedure_name = upper('sp_test');
    commit;

    set term ^;
    alter procedure sp_test(whoami rdb$user) returns(memo_info rdb$description) as
    begin
        memo_info = 'bar';
        suspend;
    end
    ^
    set term ;^
    commit;

    select 'point-3' as msg, rdb$parameter_name, rdb$parameter_type, rdb$field_source 
    from rdb$procedure_parameters 
    where rdb$procedure_name = upper('sp_test')
    order by rdb$parameter_name, rdb$parameter_type;

    select 'point-4' as msg, rdb$procedure_source 
    from rdb$procedures 
    where rdb$procedure_name = upper('sp_test');
    commit;

    drop procedure sp_test;
    commit;

    -- no rows must be issued:
    select 'point-5' as msg, rdb$parameter_name, rdb$parameter_type, rdb$field_source 
    from rdb$procedure_parameters 
    where rdb$procedure_name = upper('sp_test');

    -- no rows must be issued:
    select 'point-6' as msg, rdb$procedure_source 
    from rdb$procedures 
    where rdb$procedure_name = upper('sp_test');
    commit;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             point-1
    RDB$PARAMETER_NAME              INFO
    RDB$PARAMETER_TYPE              1
    RDB$FIELD_SOURCE                RDB$SOURCE
    Records affected: 1


    MSG                             point-2
    RDB$PROCEDURE_SOURCE            1a:1e0
    begin
    info = 'foo';
    suspend;
    end
    Records affected: 1


    MSG                             point-3
    RDB$PARAMETER_NAME              MEMO_INFO
    RDB$PARAMETER_TYPE              1
    RDB$FIELD_SOURCE                RDB$DESCRIPTION

    MSG                             point-3
    RDB$PARAMETER_NAME              WHOAMI
    RDB$PARAMETER_TYPE              0
    RDB$FIELD_SOURCE                RDB$USER
    Records affected: 2
    

    MSG                             point-4
    RDB$PROCEDURE_SOURCE            1a:1e3
    begin
    memo_info = 'bar';
    suspend;
    end
    Records affected: 1

    Records affected: 0

    Records affected: 0
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

