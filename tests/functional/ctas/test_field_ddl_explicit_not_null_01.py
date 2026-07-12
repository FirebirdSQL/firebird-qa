#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9053
TITLE:       CTAS. Nullability in case when column is declared via nullable domain but has explicit 'own' NOT-null flag in the declaration.
DESCRIPTION:
    Check that field declared explicitly as 'NOT null' will have such attribute in the target table.
NOTES:
    [12.07.2026] pzotov
    See: https://groups.google.com/g/firebird-devel/c/fG1lL9Kz1iU/m/QqxubCMAAgAJ
    Currently only one datatype is checked: int.
    Confirmed bug on 6.0.0.2070-d2cb23c.
    Fix: https://github.com/FirebirdSQL/firebird/commit/183d48b3d461ef350d546ea557aba6e5dbd926b2
    Checked on 6.0.0.2072-42c8a5d
"""

import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    test_script = f"""
        set bail on;
        set blob all;
        set list on;
        set autoterm on;
        commit;

        -- https://groups.google.com/u/1/g/firebird-devel/c/fG1lL9Kz1iU
        create domain dm_not_null int NOT null;
        create domain dm_nullable int;

        recreate table tbase(
            fn_implicit_nn dm_not_null
           ,fn_explicit_nn dm_nullable NOT NULL
        );

        recreate table ctas_test as (
            select * from tbase
        );
        commit;

        select
            rf.rdb$field_name as rf_fld_name
            ,rf.rdb$null_flag as rf_not_null
        from rdb$relation_fields rf
        where rf.rdb$relation_name = upper('CTAS_TEST')
        order by rf.rdb$field_position
        ;
        commit;

        set bail OFF;
        -- following two statements must fail:
        insert into ctas_test(fn_implicit_nn, fn_explicit_nn) values (null, 1);
        insert into ctas_test(fn_implicit_nn, fn_explicit_nn) values (1, null);
    """

    act.expected_stdout = """
        RF_FLD_NAME FN_IMPLICIT_NN
        RF_NOT_NULL 1
        RF_FLD_NAME FN_EXPLICIT_NN
        RF_NOT_NULL 1

        Statement failed, SQLSTATE = 23000
        validation error for column "PUBLIC"."CTAS_TEST"."FN_IMPLICIT_NN", value "*** null ***"
        
        Statement failed, SQLSTATE = 23000
        validation error for column "PUBLIC"."CTAS_TEST"."FN_EXPLICIT_NN", value "*** null ***"
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
