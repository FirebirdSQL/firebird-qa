#coding:utf-8
#
# id:           bugs.core_2685
# title:        System triggers on view with check option are not removed
# decription:   
# tracker_id:   CORE-2685
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Updated code: made STDOUT independent of Firebird version
    -- Note about SIMILAR TO: one need here to specify backslash TWICE inside escape clause,
    -- e.g: ... escape '\\' (fbt_run feature ?)
    set list on;
    set width dep_name1 10;
    set width dep_name2 10;
    set width dep_name3 10;
    set width dep_name4 10;
    
    create or alter view v1 as select 1 id from rdb$database;
    commit;
    recreate table test_table (id integer, caption varchar(10));
    
    ------ block 1 -----
    
    create or alter view v1 as
    select id, caption from test_table where id > 0;
    commit;
    
    select upper(left(rdb$dependent_name,5)) dep_name1 
    from rdb$database b
    left join rdb$dependencies d on 
        d.rdb$depended_on_name = upper( 'v1' )
        and trim(d.rdb$dependent_name) similar to upper('check\\_[[:digit:]]+') escape '\\'
    ;
    
    ------ block 2 -----
    
    create or alter view v1 as select id ,caption from test_table where id > 0
    with check option;
    commit;
    
    select upper(left(rdb$dependent_name,5)) dep_name2 
    from rdb$database
    left join rdb$dependencies d on
        d.rdb$depended_on_name = upper( 'v1' )
        and trim(d.rdb$dependent_name) similar to upper('check\\_[[:digit:]]+') escape '\\'
    ;
    ------ block 3 -----
    
    create or alter view v1 as select id, caption from test_table where id > 0
    with check option;
    
    create or alter view v1 as select id, caption from test_table where id > 0
    with check option;
    
    create or alter view v1 as select id,caption from test_table where id > 0
    with check option;
    commit;
    select upper(left(rdb$dependent_name,5)) dep_name3 
    from rdb$database
    left join rdb$dependencies d on 
        d.rdb$depended_on_name = upper( 'v1' )
        and trim(d.rdb$dependent_name) similar to upper('check\\_[[:digit:]]+') escape '\\'
    ;
    
    ------ block 4 -----
    
    create or alter view v1 as select id,caption from test_table where id > 0;
    create or alter view v1 as select id from test_table where id > 0;
    commit;
    
    select upper(left(rdb$dependent_name,5)) dep_name4 
    from rdb$database
    left join rdb$dependencies d on 
        d.rdb$depended_on_name = upper( 'v1' )
        and trim(d.rdb$dependent_name) similar to upper('check\\_[[:digit:]]+') escape '\\'
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DEP_NAME1                       <null>
    DEP_NAME2                       CHECK
    DEP_NAME2                       CHECK
    DEP_NAME2                       CHECK
    DEP_NAME3                       CHECK
    DEP_NAME3                       CHECK
    DEP_NAME3                       CHECK
    DEP_NAME4                       <null> 
  """

@pytest.mark.version('>=2.5.0')
def test_core_2685_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

