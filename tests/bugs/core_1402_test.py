#coding:utf-8
#
# id:           bugs.core_1402
# title:        CREATE VIEW without column list when UNION is used
# decription:   
# tracker_id:   CORE-1402
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('V_SOURCE.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate view V1 as
    select d.rdb$relation_id from rdb$database d
    union all
    select d.rdb$relation_id from rdb$database d;
    
    recreate view V2 as
    select d.rdb$relation_id as q from rdb$database d
    union all
    select d.rdb$relation_id as w from rdb$database d;
    
    recreate view V3 as
    select a from (select 1 a from rdb$database)
    union all
    select b from (select 1 b from rdb$database);
    
    recreate view V4 as
    select a as a1 from (select 1 a from rdb$database)
    union all
    select b as b1 from (select 1 b from rdb$database);
    commit;
    
    set blob all;
    set list on;

    -- Removed 'show view' commands because of core-4782 (failed on windows builds when connection charset = UTF8).
    -- Added checking query to RDB$ tables instead that views indeed DO have fields of proper type (7=smallint, 8=int):
    select
        r.rdb$relation_name v_name,
        r.rdb$view_source v_source,
        f.rdb$field_name f_name,
        ff.rdb$field_type f_type
    from rdb$relations r
    join rdb$relation_fields f using (rdb$relation_name)
    join rdb$fields ff on f.rdb$field_source = ff.rdb$field_name
    where
    r.rdb$relation_type = 1
    and r.rdb$relation_name in ('V1','V2','V3','V4')
    order by v_name, f_name;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    V_NAME                          V1
    V_SOURCE                        6:1e8
    select d.rdb$relation_id from rdb$database d
    union all
    select d.rdb$relation_id from rdb$database d
    F_NAME                          RDB$RELATION_ID
    F_TYPE                          7
    
    V_NAME                          V2
    V_SOURCE                        6:1eb
    select d.rdb$relation_id as q from rdb$database d
    union all
    select d.rdb$relation_id as w from rdb$database d
    F_NAME                          Q
    F_TYPE                          7
    
    V_NAME                          V3
    V_SOURCE                        6:2ce
    select a from (select 1 a from rdb$database)
    union all
    select b from (select 1 b from rdb$database)
    F_NAME                          A
    F_TYPE                          8
    
    V_NAME                          V4
    V_SOURCE                        6:2d1
    select a as a1 from (select 1 a from rdb$database)
    union all
    select b as b1 from (select 1 b from rdb$database)
    F_NAME                          A1
    F_TYPE                          8
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

