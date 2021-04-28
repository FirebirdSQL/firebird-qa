#coding:utf-8
#
# id:           bugs.core_1550_postfix
# title:        Unnecessary index scan happens when the same index is mapped to both WHERE and ORDER BY clauses
# decription:   
#                   http://sourceforge.net/p/firebird/code/60368
#                   Date: 2014-12-16 11:40:42 +0000 (Tue, 16 Dec 2014)
#                   
#                   First letter to dimitr: 30.09.2014 20:01.
#                   Reproduced on 3.0.0.31472 Beta 2 (10.dec.2014).
#                   Checked on:
#                       3.0.3.32837: OK, 1.516s.
#                       3.0.3.32838: OK, 0.953s.
#                       4.0.0.800: OK, 1.625s.
#                       4.0.0.801: OK, 1.125s.
#                
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- sent to dimitr 30.09.14 at 22:09
    set term ^;
    execute block as
    begin
        execute statement 'drop sequence g';
        when any do begin end
    end^
    set term ;^
    commit;

    create sequence g; commit;
    recreate table td(id int primary key using index td_pk, f01 int, f02 int); commit;
    recreate table tm(id int); commit;

    insert into tm select gen_id(g,1) from rdb$types rows 100;
    commit;

    insert into td(id, f01, f02) select id, (select min(id) from tm), gen_id(g,1) from tm; commit;

    create index td_f01_non_unq on td(f01);
    create unique index td_f01_f02_unq on td(f01, f02); -- ### NB: compound UNIQUE index presens here beside of PK ###
    commit;

    set planonly;

    -- 1. Check for usage when only PK fields are involved:
    select *
    from tm m
    where exists(
        select * from td d where m.id = d.id 
        order by d.id --------------------------- ### this "useless" order by should prevent from bitmap creation in 3.0+
    );
    -- Ineffective plan was here:
    -- PLAN (D ORDER TD_PK INDEX (TD_PK))
    -- ...                  ^
    --                      |
    --                      +-----> BITMAP created!
     
    -- 2. Check for usage when fields from UNIQUE index are involved:
    select *
    from tm m
    where exists(
        select * from td d 
        where m.id = d.f01 and d.f02 = 10 
        order by d.f01, d.f02 ------------------- ### this "useless" order by should prevent from bitmap creation in 3.0+
    );

    -- Ineffective plan was here:
    -- PLAN (D ORDER TD_F01_F02_UNQ INDEX (TD_F01_F02_UNQ))
    -- ...                           ^
    --                               |
    --                               +-----> BITMAP created!
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (D ORDER TD_PK)
    PLAN (M NATURAL)

    PLAN (D ORDER TD_F01_F02_UNQ)
    PLAN (M NATURAL)
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

