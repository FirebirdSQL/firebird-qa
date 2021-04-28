#coding:utf-8
#
# id:           bugs.core_2293
# title:        Wrong dependent object type (RELATION) in RDB$DEPEDENCIES for VIEW's
# decription:   
# tracker_id:   CORE-2293
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter procedure p_v as begin end;
    create or alter view v (id) as select 1 id from rdb$database;
    commit;
    
    set term ^ ;
    create or alter procedure p_v as
        declare x int;
    begin
        select id from v into :x;
        select 1 from rdb$database into :x;
    end ^
    set term ; ^
    commit;
    
    set list on;
    select d.rdb$depended_on_type, t.rdb$type_name -- according to the ticket text we have to check only these two columns
    from rdb$dependencies d 
    join rdb$types t on 
        d.rdb$depended_on_type = t.rdb$type
        and t.rdb$field_name = upper('RDB$OBJECT_TYPE')
    where d.rdb$dependent_name = upper('P_V');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$DEPENDED_ON_TYPE            0
    RDB$TYPE_NAME                   RELATION                                                                                     
    RDB$DEPENDED_ON_TYPE            1
    RDB$TYPE_NAME                   VIEW                                                                                         
    RDB$DEPENDED_ON_TYPE            1
    RDB$TYPE_NAME                   VIEW                                                                                         
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

