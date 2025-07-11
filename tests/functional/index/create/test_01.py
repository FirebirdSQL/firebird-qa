#coding:utf-8

"""
ID:          index.create-01
TITLE:       CREATE INDEX
DESCRIPTION:
FBTEST:      functional.index.create.01
"""

import pytest
from firebird.qa import *

db = db_factory()

act = isql_act('db', test_script)

expected_stdout = """TEST INDEX ON T(A)"""

@pytest.mark.skip("Covered by 'test_all_cases_basic.py'")
@pytest.mark.version('>=3')
def test_1(act: Action):

    IDX_COND_SOURCE = '' if act.is_version('<5') else ',ri.rdb$condition_source as idx_cond_source'
    SQL_SCHEMA_IDX = '' if act.is_version('<6') else ',ri.rdb$schema_name as idx_schema_name'
    SQL_SCHEMA_FKEY = '' if act.is_version('<6') else ',ri.rdb$schema_name as fk_schema_name'

    test_script = f"""
        create v_index_info as
        select
             ri.rdb$index_id as idx_id
            ,ri.rdb$index_name as idx_name
            ,ri.rdb$relation_name as rel_name
            ,ri.rdb$unique_flag as idx_uniq
            ,ri.rdb$description as idx_descr
            ,ri.rdb$segment_count as idx_segm_count
            ,ri.rdb$index_inactive as idx_inactive
            ,ri.rdb$index_type as idx_type
            ,ri.rdb$foreign_key as idx_fkey
            ,ri.rdb$expression_source as idx_expr_source
            --,ri.rdb$statistics as idx_stat
            -- 5.x
            {IDX_COND_SOURCE}
            --  6.x
            {SQL_SCHEMA_IDX}
            {SQL_SCHEMA_FKEY}
            ,rs.rdb$field_name as fld_name
            ,rs.rdb$field_position as fld_pos
        from rdb$indices ri
        join rdb$index_segments rs on ri.rdb$index_name = rs.rdb$index_name
        where coalesce(ri.rdb$system_flag,0) = 0 and ri.rdb$index_name starting with 'TEST_'
        order by ri.rdb$relation_name, ri.rdb$index_name, rs.rdb$field_position
        ;    
        commit;
        create table test(f01 int);
        create index test_f01 on test(f01);
    """

    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
