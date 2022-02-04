#coding:utf-8

"""
ID:          optimizer.full-join-02
TITLE:       FULL OUTER JOIN,  list all values, but filtered in WHERE clause
DESCRIPTION:
  TableX FULL OUTER JOIN TableY with relation in the ON clause.
  Three tables are used, where 1 table (RC) holds references to the two other tables (R and C).
  The two tables R and C contain both 1 value that isn't inside RC.
NOTES:
[27.12.2020]
  added 'rc.categoryid' to 'order by' list in order to have always stable sort result.
  Mismatch with expected result due to different position of records with the same 'rc.relationid'
  occured on 4.0.0.2298. CHecked on 4.0.0.2303.
FBTEST:      functional.arno.optimizer.opt_full_join_02
"""

import pytest
from firebird.qa import *

init_script = """
    create table relations (
        relationid integer,
        relationname varchar(35)
    );

    create table categories (
        categoryid integer,
        description varchar(20)
    );

    create table relationcategories (
        relationid integer,
        categoryid integer
    );
    commit;

    insert into relations (relationid, relationname) values (1, 'diving snorkel shop');
    insert into relations (relationid, relationname) values (2, 'bakery garbage');
    insert into relations (relationid, relationname) values (3, 'racing turtle');
    insert into relations (relationid, relationname) values (4, 'folding air-hook shop');

    insert into categories (categoryid, description) values (1, 'relation');
    insert into categories (categoryid, description) values (2, 'debtor');
    insert into categories (categoryid, description) values (3, 'creditor');
    insert into categories (categoryid, description) values (4, 'newsletter');

    insert into relationcategories (relationid, categoryid) values (1, 1);
    insert into relationcategories (relationid, categoryid) values (2, 1);
    insert into relationcategories (relationid, categoryid) values (3, 1);
    insert into relationcategories (relationid, categoryid) values (1, 2);
    insert into relationcategories (relationid, categoryid) values (2, 2);
    insert into relationcategories (relationid, categoryid) values (1, 3);
    commit;

    -- normally these indexes are created by the primary/foreign keys,
    -- but we don't want to rely on them for this test
    create unique asc index pk_relations on relations (relationid);
    create unique asc index pk_categories on categories (categoryid);
    create unique asc index pk_relationcategories on relationcategories (relationid, categoryid);
    create asc index fk_rc_relations on relationcategories (relationid);
    create asc index fk_rc_categories on relationcategories (categoryid);
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set plan on;
    --set list on;

    --full join should return ...
    select
        r.relationname,
        rc.relationid,
        rc.categoryid,
        c.description
    from
        relations r
        full join relationcategories rc on (rc.relationid = r.relationid)
        full join categories c on (c.categoryid = rc.categoryid)
    where
        r.relationid >= 2
    order by
         rc.relationid desc
        ,rc.categoryid
    ;
"""

act = isql_act('db', test_script, substitutions=[('=', ''), ('[ \t]+', ' ')])

expected_stdout = """
    PLAN SORT (JOIN (JOIN (C NATURAL, JOIN (JOIN (RC NATURAL, R INDEX (PK_RELATIONS)), JOIN (R INDEX (PK_RELATIONS), RC INDEX (FK_RC_RELATIONS)))), JOIN (JOIN (JOIN (RC NATURAL, R INDEX (PK_RELATIONS)), JOIN (R INDEX (PK_RELATIONS), RC INDEX (FK_RC_RELATIONS))), C NATURAL)))

    RELATIONNAME                          RELATIONID   CATEGORYID DESCRIPTION
    =================================== ============ ============ ============
    racing turtle                                  3            1 relation
    bakery garbage                                 2            1 relation
    bakery garbage                                 2            2 debtor
    folding air-hook shop                     <null>       <null> <null>
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
