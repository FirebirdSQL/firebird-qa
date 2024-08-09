#coding:utf-8

"""
ID:          domain.create-17
FBTEST:      functional.domain.create.17
TITLE:       CREATE DOMAIN using 'CHARACTER VARYING' keyword
DESCRIPTION: Simple domain creation based on CHARACTER VARYING datatype.
NOTES:
    [06.10.2023] pzotov
    1. Removed SHOW command for check result because its output often changes.
       It is enough for this test to obtain similar data from RDB tables.
    2. Made example more complex: create domain with charset differ than default one for DB, and collate differ than default for domain.
    3. Ensure that we can use just created domain w/o problem (create table with column based on domain and add record).
"""

import pytest
from firebird.qa import *

db = db_factory(charset = 'win1250')

DM_SIZE = 32765

test_script = f"""
    set bail on;
    set list on;
    alter character set win1252 set default collation pxw_swedfin;
    create view v_domain_info as
    select
        f.rdb$field_name as dm_name
        ,f.rdb$field_length as dm_size
        ,f.rdb$field_scale
        ,f.rdb$character_length as dm_char_len
        --,f.rdb$character_set_id as dm_cset_id
        --,f.rdb$collation_id as dm_coll_id
        ,f.rdb$default_source as dm_default
        ,f.rdb$null_flag as dm_not_null
        ,f.rdb$validation_source as dm_check_expr
        ,c.rdb$character_set_name as dm_cset_name
        --,c.rdb$default_collate_name as dm_default_coll_name
        --,k.rdb$base_collation_name
        ,k.rdb$collation_name as dm_coll_name
    from rdb$fields f
    join rdb$character_sets c on f.rdb$character_set_id = c.rdb$character_set_id
    join rdb$collations k on c.rdb$character_set_id = k.rdb$character_set_id and f.rdb$collation_id = k.rdb$collation_id
    where f.rdb$field_name = upper('dm_test')
    ;
    commit;
    create domain dm_test CHARACTER VARYING({DM_SIZE}) character set win1252 collate win_ptbr;
    commit;
    select v.* from v_domain_info v;

    -- Ensure that we can use this domain w/o problem:
    recreate table test(s dm_test);
    commit;
    insert into test(s) values( lpad('', {DM_SIZE}, uuid_to_char(gen_uuid()))) returning octet_length(s) as inserted_record_octet_length;
"""

act = isql_act('db', test_script)

expected_stdout = f"""
    DM_NAME                         DM_TEST
    DM_SIZE                         {DM_SIZE}
    RDB$FIELD_SCALE                 0
    DM_CHAR_LEN                     {DM_SIZE}
    DM_DEFAULT                      <null>
    DM_NOT_NULL                     <null>
    DM_CHECK_EXPR                   <null>
    DM_CSET_NAME                    WIN1252
    DM_COLL_NAME                    WIN_PTBR
    INSERTED_RECORD_OCTET_LENGTH    {DM_SIZE}
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
