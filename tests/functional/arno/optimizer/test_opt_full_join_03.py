#coding:utf-8

"""
ID:          optimizer.full-join-03
TITLE:       FULL OUTER JOIN,  list all values, but filtered in WHERE clause
DESCRIPTION:
  TableX FULL OUTER JOIN TableY with relation in the ON clause.
  Three tables are used, where 1 table (RC) holds references to the two other tables (R and C).
  The two tables R and C contain both 1 value that isn't inside RC.
FBTEST:      functional.arno.optimizer.opt_full_join_03
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

    -- Normally these indexes are created by the primary/foreign keys,
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
    set list on;
    -- full join should return ...
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
        c.categoryid >= 2
    order by
        rc.categoryid desc;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN SORT (JOIN (JOIN (C INDEX (PK_CATEGORIES), JOIN (JOIN (RC NATURAL, R INDEX (PK_RELATIONS)), JOIN (R NATURAL, RC INDEX (FK_RC_RELATIONS)))), JOIN (JOIN (JOIN (RC NATURAL, R INDEX (PK_RELATIONS)), JOIN (R NATURAL, RC INDEX (FK_RC_RELATIONS))), C INDEX (PK_CATEGORIES))))

    RELATIONNAME                    diving snorkel shop
    RELATIONID                      1
    CATEGORYID                      3
    DESCRIPTION                     creditor
    RELATIONNAME                    diving snorkel shop
    RELATIONID                      1
    CATEGORYID                      2
    DESCRIPTION                     debtor
    RELATIONNAME                    bakery garbage
    RELATIONID                      2
    CATEGORYID                      2
    DESCRIPTION                     debtor
    RELATIONNAME                    <null>
    RELATIONID                      <null>
    CATEGORYID                      <null>
    DESCRIPTION                     newsletter
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
