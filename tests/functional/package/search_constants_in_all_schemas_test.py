#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/812413420e110cb77cdd9688b888f5e1ff9e3d1e
TITLE:       Search existing package constants in all SCHEMAs
DESCRIPTION:
NOTES:
    [05.07.2026] pzotov
    https://groups.google.com/g/firebird-devel/c/RhAZUvc5J24/m/Dd2tHGptAQAJ
    *** deferred, need to be clarified ***
"""

import pytest
from firebird.qa import *

COMPLETED_MSG = 'Ok'
test_sql = f"""
    set bail on;
    set heading off;
    set autoddl off;
    set autoterm on;

    create package pg_test as
    begin
        constant phone varchar(12) = '+33610011111';
    end
    ;

    create schema stock;
    create schema shops;
    create schema salary;

    create package stock.pg_test as
    begin
        constant phone varchar(12) = '+33620022222';
    end
    ;

    create package shops.pg_test as
    begin
        constant phone varchar(12) = '+33630033333';
    end
    ;

    create package salary.pg_test as
    begin
        constant boss_income int = 4000000;
    end
    ;

    set search_path to public;
    select pg_test.phone from rdb$database;

    set search_path to stock;
    select pg_test.phone from rdb$database;

    set search_path to shops;
    select pg_test.phone from rdb$database;

    grant usage on package salary.pg_test to PUBLIC;
    commit;

    -- set search_path to salary; -------------- [ 1 ]
    select pg_test.boss_income from rdb$database;
    
"""

db = db_factory()
act = isql_act('db', test_sql)

@pytest.mark.skip("Deferred, need to be clarified")
@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = f"""
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
