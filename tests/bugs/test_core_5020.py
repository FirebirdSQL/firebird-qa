#coding:utf-8
#
# id:           bugs.core_5020
# title:        Regression: ORDER BY clause on compound index may disable usage of other indices
# decription:   
# tracker_id:   CORE-5020
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table zf(
        id integer not null primary key,
        kont_id integer not null
    );

    recreate table u(
        id integer not null primary key,
        kont_id integer not null
    );

    recreate table k(
        id integer not null primary key
    );

    commit;

    insert into zf (id, kont_id) values ('1', '1');
    insert into zf (id, kont_id) values ('2', '7');
    insert into zf (id, kont_id) values ('3', '3');
    insert into zf (id, kont_id) values ('4', '5');
    insert into zf (id, kont_id) values ('5', '5');
    insert into zf (id, kont_id) values ('6', '1');
    insert into zf (id, kont_id) values ('7', '4');
    insert into zf (id, kont_id) values ('8', '2');
    insert into zf (id, kont_id) values ('9', '9');
    insert into zf (id, kont_id) values ('10', '1');


    insert into k (id) values ('1');
    insert into k (id) values ('2');
    insert into k (id) values ('3');
    insert into k (id) values ('4');
    insert into k (id) values ('5');
    insert into k (id) values ('6');
    insert into k (id) values ('7');
    insert into k (id) values ('8');
    insert into k (id) values ('9');
    insert into k (id) values ('10');

    insert into u (id, kont_id) values ('1', '4');
    insert into u (id, kont_id) values ('2', '6');
    insert into u (id, kont_id) values ('3', '3');
    insert into u (id, kont_id) values ('4', '2');
    insert into u (id, kont_id) values ('5', '5');
    insert into u (id, kont_id) values ('6', '2');
    insert into u (id, kont_id) values ('7', '9');
    insert into u (id, kont_id) values ('8', '2');
    insert into u (id, kont_id) values ('9', '10');
    insert into u (id, kont_id) values ('10', '1');

    commit;

    alter table zf add constraint fk_zf__k 
    	foreign key(kont_id) 
    	references k(id) 
    	using index fk_zf__k
    ; 
    set statistics index fk_zf__k;

    create index ixa_fk__id__kont_id on zf(id, kont_id);
    commit;

    set planonly;
    select zf.*
    from zf
    where zf.kont_id=5
    order by zf.id, kont_id;

    -- Plan in 3.0.0.32179 (before fix): PLAN (ZF ORDER IXA_FK__ID__KONT_ID)
    -- Fixed in 3.0 since: http://sourceforge.net/p/firebird/code/62570
    -- Checked on 2.5.5.26952 - plans are the same now.

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (ZF ORDER IXA_FK__ID__KONT_ID INDEX (FK_ZF__K))
  """

@pytest.mark.version('>=2.5')
def test_core_5020_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

