#coding:utf-8

"""
ID:          issue-3481-3651
ISSUE:       3481, 3651
TITLE:       BAD PLAN with using LEFT OUTER JOIN in SUBSELECT
DESCRIPTION:
  Ticket subj: Select statement with more non indexed reads in version 2.5RC3 as in version 2.1.3
JIRA:        CORE-3103
FBTEST:      bugs.core_3103
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    execute block as
    begin
      begin execute statement 'drop sequence g'; when any do begin end end
    end
    ^
    set term ;^
    commit;
    create sequence g;
    commit;

    recreate table bauf(id int);
    commit;
    recreate table bstammdaten(
        id int, maskenkey varchar(10),
        constraint tmain_pk primary key(id) using index bstammdaten_id_pk
    );
    commit;
    recreate table bauf(
        id int
        ,bstammdaten_id_maskenkey int
        ,constraint tdetl_pk primary key(id) using index bauf_pk
        ,constraint tdetl_fk foreign key (bstammdaten_id_maskenkey)
         references bstammdaten(id)
         using index fk_bauf_bstammdaten_id
    );
    commit;

    set term ^;
    execute block as
        declare n_main int = 5000; --  42000;
        declare i int = 0;
    begin
        while ( i < n_main ) do
        begin
            insert into bstammdaten(id, maskenkey) values(:i, iif(:i < :n_main / 100, '53', cast(rand()*100 as int) ) );
            insert into bauf(id, bstammdaten_id_maskenkey) values (gen_id(g,1), :i);
            if ( rand() < 0.8 ) then
                insert into bauf(id, bstammdaten_id_maskenkey) values (gen_id(g,1), :i);
            i = i + 1;
        end
    end
    ^set term ;^
    commit;

    create index bstammdaten_maskenkey on bstammdaten(maskenkey);
    commit;
    set statistics index fk_bauf_bstammdaten_id;
    set statistics index bstammdaten_id_pk;
    commit;


    set planonly;
    select count(*) from bauf
    where id =
    (
        select max(b.id) from bstammdaten a
        left outer join bauf b on b.bstammdaten_id_maskenkey = a.id
        where a.maskenkey='53'
    );
    commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN JOIN (A INDEX (BSTAMMDATEN_MASKENKEY), B INDEX (FK_BAUF_BSTAMMDATEN_ID))
    PLAN (BAUF INDEX (BAUF_PK))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

