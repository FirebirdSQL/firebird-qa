#coding:utf-8
#
# id:           bugs.core_3174
# title:        Expression index with TRIM may lead to incorrect indexed lookup
# decription:   
# tracker_id:   CORE-3174
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """
    create collation ps_yes for utf8 from unicode pad space;
    create collation ps_no  for utf8 from unicode no pad;

    create table t (id int, c_pad varchar(10), c_nopad varchar(10) character set utf8 collate ps_no);
    commit;
    insert into t(id, c_pad, c_nopad) values (1, '123',    '123');
    insert into t(id, c_pad, c_nopad) values (2, ' 123',   ' 123');
    insert into t(id, c_pad, c_nopad) values (3, '123  ',  '123  ');
    insert into t(id, c_pad, c_nopad) values (4, ' 123  ', ' 123  ');
    commit;

    create index t_c_pad_trim_right on t computed by (trim(trailing from c_pad));
    create index t_c_pad_trim_left on t computed by (trim(leading from c_pad));
    create index t_c_nopad_trim_right on t computed by (trim(trailing from c_nopad));
    create index t_c_nopad_trim_left on t computed by (trim(leading from c_nopad));
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set plan on;
    --set echo on;

    select '1.a' as test_no, id,'.' || c_pad || '.' as c_pad from t where trim(c_pad) = '123';
    select '1.b' as test_no, id,'.' || c_pad || '.' as c_pad from t where trim(trailing from c_pad) = trim(leading from c_pad);
    select '1.c' as test_no, id,'.' || c_pad || '.' as c_pad from t where trim(trailing from c_pad) = '123';
    select '1.d' as test_no, id,'.' || c_pad || '.' as c_pad from t where trim(leading from c_pad) = '123';
    select '1.e' as test_no, id,'.' || c_pad || '.' as c_pad from t where trim(trailing from c_pad) starting with '123';
    select '1.f' as test_no, id,'.' || c_pad || '.' as c_pad from t where trim(leading from c_pad) starting with '123';

    -------------------------------------------------------------------------

    select '2.a' as test_no, id,'.' || c_nopad || '.' as c_nopad from t where trim(c_nopad) = '123';
    select '2.b' as test_no, id,'.' || c_nopad || '.' as c_nopad from t where trim(trailing from c_nopad) = trim(leading from c_nopad);
    select '2.c' as test_no, id,'.' || c_nopad || '.' as c_nopad from t where trim(trailing from c_nopad) = '123';
    select '2.d' as test_no, id,'.' || c_nopad || '.' as c_nopad from t where trim(leading from c_nopad) = '123';
    select '2.f' as test_no, id,'.' || c_nopad || '.' as c_nopad from t where trim(trailing from c_nopad) starting with '123';
    select '2.g' as test_no, id,'.' || c_nopad || '.' as c_nopad from t where trim(leading from c_nopad) starting with '123';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (T NATURAL)
    
    TEST_NO           ID C_PAD
    ======= ============ ============
    1.a                1 .123.
    1.a                2 . 123.
    1.a                3 .123  .
    1.a                4 . 123  .
    
    
    PLAN (T NATURAL)
    
    TEST_NO           ID C_PAD
    ======= ============ ============
    1.b                1 .123.
    1.b                3 .123  .
    
    
    PLAN (T INDEX (T_C_PAD_TRIM_RIGHT))
    
    TEST_NO           ID C_PAD
    ======= ============ ============
    1.c                1 .123.
    1.c                3 .123  .
    
    
    PLAN (T INDEX (T_C_PAD_TRIM_LEFT))
    
    TEST_NO           ID C_PAD
    ======= ============ ============
    1.d                1 .123.
    1.d                2 . 123.
    1.d                3 .123  .
    1.d                4 . 123  .
    
    
    PLAN (T INDEX (T_C_PAD_TRIM_RIGHT))
    
    TEST_NO           ID C_PAD
    ======= ============ ============
    1.e                1 .123.
    1.e                3 .123  .
    
    
    PLAN (T INDEX (T_C_PAD_TRIM_LEFT))
    
    TEST_NO           ID C_PAD
    ======= ============ ============
    1.f                1 .123.
    1.f                2 . 123.
    1.f                3 .123  .
    1.f                4 . 123  .
    
    
    PLAN (T NATURAL)
    
    TEST_NO           ID C_NOPAD
    ======= ============ ================================================
    2.a                1 .123.
    2.a                2 . 123.
    2.a                3 .123  .
    2.a                4 . 123  .
    
    
    PLAN (T NATURAL)
    
    TEST_NO           ID C_NOPAD
    ======= ============ ================================================
    2.b                1 .123.
    
    
    PLAN (T INDEX (T_C_NOPAD_TRIM_RIGHT))
    
    TEST_NO           ID C_NOPAD
    ======= ============ ================================================
    2.c                1 .123.
    2.c                3 .123  .
    
    
    PLAN (T INDEX (T_C_NOPAD_TRIM_LEFT))
    
    TEST_NO           ID C_NOPAD
    ======= ============ ================================================
    2.d                1 .123.
    2.d                2 . 123.
    
    
    PLAN (T INDEX (T_C_NOPAD_TRIM_RIGHT))
    
    TEST_NO           ID C_NOPAD
    ======= ============ ================================================
    2.f                1 .123.
    2.f                3 .123  .
    
    
    PLAN (T INDEX (T_C_NOPAD_TRIM_LEFT))
    
    TEST_NO           ID C_NOPAD
    ======= ============ ================================================
    2.g                1 .123.
    2.g                2 . 123.
    2.g                3 .123  .
    2.g                4 . 123  .
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

