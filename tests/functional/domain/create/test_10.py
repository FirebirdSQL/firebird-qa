#coding:utf-8

"""
ID:          domain.create-10
FBTEST:      functional.domain.create.10
TITLE:       CREATE DOMAIN - TIMESTAMP ARRAY
DESCRIPTION: Array domain creation based TIMESTAMP datatype
"""

import pytest
from firebird.qa import *

db = db_factory()

    set list on;
    set count on;
    create view v_domain_info as
    select
        f.rdb$field_name as dm_name
        ,f.rdb$field_length as dm_size
        ,f.rdb$field_scale as dm_scale
        ,f.rdb$field_precision dm_prec
        ,f.rdb$field_type as dm_type
        ,f.rdb$field_sub_type as dm_subt
        ,f.rdb$dimensions as dm_dimens
        ,f.rdb$null_flag as dm_null
        ,f.rdb$validation_source as dm_check_expr
        ,f.rdb$character_length as dm_char_len
        ,f.rdb$character_set_id as dm_cset_id
        ,f.rdb$collation_id as dm_coll_id
        ,c.rdb$character_set_name as dm_cset_name
        ,c.rdb$default_collate_name as dm_default_coll_name
        ,k.rdb$base_collation_name
        ,k.rdb$collation_name as dm_coll_name
    from rdb$fields f
    left join rdb$character_sets c on f.rdb$character_set_id = c.rdb$character_set_id
    left join rdb$collations k on c.rdb$character_set_id = k.rdb$character_set_id and f.rdb$collation_id = k.rdb$collation_id
    where f.rdb$field_name = upper('dm_test')
    ;
    CREATE DOMAIN test TIMESTAMP [1024];
    commit;
    select * from v_domain_info;
test_script = """


SHOW DOMAIN test;"""

act = isql_act('db', test_script)

expected_stdout = """TEST                            ARRAY OF [1024]
TIMESTAMP Nullable"""

@pytest.mark.skip("Covered by 'test_all_datatypes_basic.py'")
@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
