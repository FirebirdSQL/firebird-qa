#coding:utf-8
#
# id:           bugs.core_3881
# title:        Extend the error reported for index/constraint violations to include the problematic key value
# decription:   
# tracker_id:   CORE-3881
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = [('-At trigger.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table tmain(
        id int constraint tmain_pk primary key using index tmain_pk
        ,mka int
        ,mkb int
        ,constraint tmain_mka_mkb_constraint_unq unique(mka, mkb) using index tmain_mka_mkb_constraint_unq
        ,constraint tmain_fka foreign key (mka) references tmain(id) on update set null using index tmain_fka
        ,constraint tmain_fkb foreign key (mkb) references tmain(id) on update set null using index tmain_fkb
    );
    create unique descending index tmain_difference_unq_idx on tmain computed by( (coalesce(mka,0) - coalesce(mkb,0)) );
    commit;

    insert into tmain(id, mka, mkb) values( 100, 100,  null);
    insert into tmain(id, mka, mkb) values( 200, null, 200);
    insert into tmain(id, mka, mkb) values( 300, 200, null);
    commit;


    -- This statement should violate primary key constraint:
    insert into tmain(id, mka, mkb) select 600-id, 600-id, mkb from tmain where id<>200;

    -- This will violate unique constraint `tmain_mka_mkb_constraint_unq` defined on two nullable fields:(mka, mkb):
    insert into tmain(id, mka, mkb) values(500, null,200);

    -- This will violate unique computed-by index `tmain_difference_unq_idx` because NULLS are treated in its expression as ZEROES:
    update tmain set mka=null, mkb=null;

    -- This will violate unique constraint `tmain_mka_mkb_constraint_unq` defined on two nullable fields:(mka, mkb):
    update tmain set mka=coalesce(mka, 200), mkb=coalesce(mkb, 200);

    -- This will force CASCADE trigger to make updating values in fields `mka` and `mkb` to NULLS.
    -- But it means that these NULLS will be treated as ZEROEs in expression of computed-by index `tmain_difference_unq_idx`
    -- and thus again will violate its uniquness:
    update tmain set id=0 where id=200;  -- uniq idx tmain_difference_unq_idx, At trigger 'CHECK_nn'
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TMAIN_PK" on table "TMAIN"
    -Problematic key value is ("ID" = 300)

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TMAIN_MKA_MKB_CONSTRAINT_UNQ" on table "TMAIN"
    -Problematic key value is ("MKA" = NULL, "MKB" = 200)

    Statement failed, SQLSTATE = 23000
    attempt to store duplicate value (visible to active transactions) in unique index "TMAIN_DIFFERENCE_UNQ_IDX"
    -Problematic key value is (<expression> = 0)

    Statement failed, SQLSTATE = 23000
    violation of PRIMARY or UNIQUE KEY constraint "TMAIN_MKA_MKB_CONSTRAINT_UNQ" on table "TMAIN"
    -Problematic key value is ("MKA" = 200, "MKB" = 200)

    Statement failed, SQLSTATE = 23000
    attempt to store duplicate value (visible to active transactions) in unique index "TMAIN_DIFFERENCE_UNQ_IDX"
    -Problematic key value is (<expression> = 0)
    -At trigger 'CHECK_2'
  """

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

