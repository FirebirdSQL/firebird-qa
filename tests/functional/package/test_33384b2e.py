#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/33384b2ee2d36fcab3aa34245a328b0401eb687b
TITLE:       Packaged temporary tables. Only `INSERT` is allowed for them in the package body units
DESCRIPTION:
    Test verifies that unit belonging to package can run INSERT/UPDATE/DELETE/MERGE against both
    public and private packaged temporary tables.
NOTES:
    https://groups.google.com/g/firebird-devel/c/IGAsQtQ5cFM/m/vEeqrVspAwAJ
    Confirmed bug on 6.0.0.1971-79b12a6.
    Checked on 6.0.0.1976-33384b2
"""

import pytest
from firebird.qa import *

test_sql = f"""
    set bail on;
    set autoterm on;
    create or alter package pg_test as
    begin
        temporary table pkt_open(id int) on commit preserve rows index pkt_open_id(id);
    end
    ;

    recreate package body pg_test as
    begin
        temporary table pkt_priv(id int) on commit preserve rows desc index pkt_priv_id(id);
        procedure sp_modify_data as
        begin
            insert into pkt_open(id) select i from generate_series(1, 20) as s(i);
            insert into pkt_priv(id) select i from generate_series(1, 20) as s(i);

            merge into pkt_open t
            using (select id from pkt_priv order by id desc rows 5) s on s.id = t.id
            when MATCHED then update set id = -1000 - s.id
            ;

            merge into pkt_priv t
            using (select id from pkt_open order by id desc rows 5) s on s.id = t.id
            when MATCHED then update set id = 1000 + s.id
            ;

            update pkt_open set id = -id where id > 17;
            update pkt_priv set id = -id where id < 11;
            
            update or insert into pkt_open(id) values(-99) matching(id);
            update or insert into pkt_priv(id) values(99) matching(id);

            delete from pkt_open where id > 9;
            delete from pkt_priv where id < 13;
        end

        procedure sp_show_data returns(src varchar(10), id int) as
        begin
            for 
                select src,id
                from (
                    select 'pkt_open' src, id from pkt_open
                    UNION ALL
                    select 'pkt_priv', id from pkt_priv
                )
                order by src,id
            into
                src,id
            do
                suspend;
        end
    end
    ;

    execute procedure pg_test.sp_modify_data;

    set list on;
    set count on;
    select * from pg_test.sp_show_data;
"""

db = db_factory()
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_sql, substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = f"""
        SRC                             pkt_open
        ID                              -1020
        SRC                             pkt_open
        ID                              -1019
        SRC                             pkt_open
        ID                              -1018
        SRC                             pkt_open
        ID                              -1017
        SRC                             pkt_open
        ID                              -1016
        SRC                             pkt_open
        ID                              -99
        SRC                             pkt_open
        ID                              1
        SRC                             pkt_open
        ID                              2
        SRC                             pkt_open
        ID                              3
        SRC                             pkt_open
        ID                              4
        SRC                             pkt_open
        ID                              5
        SRC                             pkt_open
        ID                              6
        SRC                             pkt_open
        ID                              7
        SRC                             pkt_open
        ID                              8
        SRC                             pkt_open
        ID                              9
        SRC                             pkt_priv
        ID                              16
        SRC                             pkt_priv
        ID                              17
        SRC                             pkt_priv
        ID                              18
        SRC                             pkt_priv
        ID                              19
        SRC                             pkt_priv
        ID                              20
        SRC                             pkt_priv
        ID                              99
        SRC                             pkt_priv
        ID                              1011
        SRC                             pkt_priv
        ID                              1012
        SRC                             pkt_priv
        ID                              1013
        SRC                             pkt_priv
        ID                              1014
        SRC                             pkt_priv
        ID                              1015
        Records affected: 26
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
