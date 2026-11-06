#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/d5995e42be7ce85ead6410f6876c5365cdc213a0
TITLE:       Fix view columns based on procedures of another schema.
DESCRIPTION:
NOTES:
    The scenario has been found by AI.
    Confirmed bug on 6.0.0.2446-0b6d977 (wrong result of query to rdb$relation_fields; crash on subsequent query to the view).
    Checked on 6.0.0.2447-77d8185.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set list on;
    set autoterm on;
    create schema s_moex;
    create schema s_nyse;
    commit;
    set search_path to s_moex;
    create procedure sp_get_deals returns (id integer not null, txt varchar(30)) as
    begin
        id=1;
        txt='one';
        suspend;
    end
    ;

    set search_path to s_nyse;
    create view v_get_deals as
    select p.id, p.txt from s_moex.sp_get_deals p
    ;

    commit;

    select rf.rdb$field_name as f_name, rf.rdb$field_source_schema_name as f_src_schema
    from rdb$relation_fields rf
    where rf.rdb$relation_name = upper('v_get_deals')
    order by 1
    ;
    commit;
    -- before fix, this query caused FB crash (checked on 6.0.0.2446-0b6d977):
    select * from s_nyse.v_get_deals;

"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    F_NAME       ID
    F_SRC_SCHEMA S_MOEX
    F_NAME       TXT
    F_SRC_SCHEMA S_MOEX
    ID           1
    TXT          one
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
