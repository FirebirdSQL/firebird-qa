#coding:utf-8
#
# id:           bugs.core_3103
# title:        BAD PLAN with using LEFT OUTER JOIN in SUBSELECT. See also: CORE-3283
# decription:   Ticket subj: Select statement with more non indexed reads in version 2.5RC3 as in version 2.1.3
# tracker_id:   CORE-3103
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN JOIN (A INDEX (BSTAMMDATEN_MASKENKEY), B INDEX (FK_BAUF_BSTAMMDATEN_ID))
    PLAN (BAUF INDEX (BAUF_PK))
  """

@pytest.mark.version('>=2.1.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

