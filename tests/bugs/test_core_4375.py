#coding:utf-8
#
# id:           bugs.core_4375
# title:        Procedure executes infinitely if contains more than 32767 statements inside any BEGIN/END block
# decription:   
# tracker_id:   CORE-4375
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    -- On Alpha2 (WI-T3.0.0.30809):
    -- Statement failed, SQLSTATE = 42000
    -- Dynamic SQL Error
    -- -SQL error code = -104
    -- -Invalid command
    -- -no column name specified for column number 1 in derived table C
    -- On Beta2 (WI-T3.0.0.31807) works OK:
    set term ^;
    execute block returns (SQL blob sub_type text) as
    begin
      select 
          'create or alter procedure test_proc returns(id integer) as 
    begin '
          || list('
        suspend; -- '||id, '')
    ||'
    end' 
    
      from (select row_number()over() id from rdb$types a, rdb$types b rows 50000) c
      into :SQL;
      execute statement :SQL;
      --suspend;
    end 
    ^
    set term ;^
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select count(*) cnt from test_proc;

    set term ^;
    execute block returns(cnt int) as
        declare v_proc_src blob;
    begin
        execute statement 'select count(*) cnt from test_proc' into cnt;
        suspend;
  
        select rdb$procedure_source from rdb$procedures where rdb$procedure_name = upper('test_proc')
        into v_proc_src;
        select octet_length(:v_proc_src) - octet_length(replace(:v_proc_src, ascii_char(10), ''))
        from rdb$database
        into cnt;
        suspend;
    end
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CNT                             50000
    CNT                             50000
    CNT                             50001
  """

@pytest.mark.version('>=3.0')
def test_core_4375_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

