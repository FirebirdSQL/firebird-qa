#coding:utf-8

"""
ID:          issue-5308
ISSUE:       5308
TITLE:       Regression: ORDER BY clause on compound index may disable usage of other indices
DESCRIPTION:
JIRA:        CORE-5020
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
    PLAN (ZF ORDER IXA_FK__ID__KONT_ID INDEX (FK_ZF__K))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

