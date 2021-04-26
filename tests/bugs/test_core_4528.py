#coding:utf-8
#
# id:           bugs.core_4528
# title:        Allow hash/merge joins for non-field (dbkey or derived expression) equalities
# decription:   NB: currently join oth three and more sources made by USING or NATURAL clauses will use NL. See CORE-4809
# tracker_id:   CORE-4528
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
    recreate table tn(x int primary key using index tn_x); 
    commit;
    insert into tn select row_number()over() from rdb$types;
    commit;
    
    -- this will NOT pruduce HJ, at least for WI-T3.0.0.31840
    -- select * from (select rdb$db_key a from tn) r join (select rdb$db_key b from tn) s on r.a||'' = s.b||''; 
    
    set planonly;
    --set echo on;
    
    -- ### 1. Columns from derived tables ###
    
    select count(*)
    from (select x a from tn) r 
    join (select x a from tn) s on r.a + 0 = s.a + 0; 
    
    select count(*)
    from (select x a from tn) r 
    join (select x a from tn) s on r.a + 0 = s.a + 0
    join (select x a from tn) t on s.a + 0 = t.a + 0; 
    
    -- ### 2. RDB$DB_KEY ###
    
    ----------- test `traditional` join  form -----------------
    select count(*)
    from (select rdb$db_key||'' a from tn) r 
    join (select rdb$db_key||'' a from tn) s on r.a = s.a;
    
    select count(*) 
    from (select rdb$db_key||'' a from tn) r 
    join (select rdb$db_key||'' a from tn) s on r.a = s.a
    join (select rdb$db_key||'' a from tn) t on s.a = t.a;
    
    select count(*) 
    from (select rdb$db_key||'' a from tn) r 
    join (select rdb$db_key||'' a from tn) s on r.a = s.a
    join (select rdb$db_key||'' a from tn) t on s.a = t.a
    join (select rdb$db_key||'' a from tn) u on t.a = u.a; 
    
    ----------- test join on named columns form -----------------
    select count(*)
    from (select rdb$db_key||'' a from tn) r 
    join (select rdb$db_key||'' a from tn) s using(a); 
    
    -- Currently these will produce NESTED LOOPS, SEE CORE-4809.
    -- Uncomment these statements and correct expected_output when
    -- (and if) core-4809 will be fixed:
    --select count(*)
    --from (select rdb$db_key||'' a from tn) r 
    --join (select rdb$db_key||'' a from tn) s using(a)
    --join (select rdb$db_key||'' a from tn) t using(a); 
    --
    --select count(*) 
    --from (select rdb$db_key||'' a from tn) r 
    --join (select rdb$db_key||'' a from tn) s using(a)
    --join (select rdb$db_key||'' a from tn) t using(a)
    --join (select rdb$db_key||'' a from tn) u using(a); 
    
    ----------- test natural join form -----------------
    
    select count(*) 
    from (select rdb$db_key||'' a from tn) r
    natural join (select rdb$db_key||'' a from tn) s; 
    
    -- Currently these will produce NESTED LOOPS, SEE CORE-4809.
    -- Uncomment these statements and correct expected_output when
    -- (and if) core-4809 will be fixed:
    --select count(*)
    --from (select rdb$db_key||'' a from tn) r
    --natural join (select rdb$db_key||'' a from tn) s
    --natural join (select rdb$db_key||'' a from tn) t;
    --
    --select count(*) 
    --from (select rdb$db_key||'' a from tn) r
    --natural join (select rdb$db_key||'' a from tn) s
    --natural join (select rdb$db_key||'' a from tn) t
    --natural join (select rdb$db_key||'' a from tn) u; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN HASH (S TN NATURAL, R TN NATURAL)
    PLAN HASH (HASH (T TN NATURAL, S TN NATURAL), R TN NATURAL)
    PLAN HASH (S TN NATURAL, R TN NATURAL)
    PLAN HASH (HASH (T TN NATURAL, S TN NATURAL), R TN NATURAL)
    PLAN HASH (HASH (HASH (U TN NATURAL, T TN NATURAL), S TN NATURAL), R TN NATURAL)
    PLAN HASH (S TN NATURAL, R TN NATURAL)
    PLAN HASH (S TN NATURAL, R TN NATURAL)
  """

@pytest.mark.version('>=3.0')
def test_core_4528_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

