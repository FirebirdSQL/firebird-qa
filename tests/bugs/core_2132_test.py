#coding:utf-8

"""
ID:          issue-2563
ISSUE:       2563
TITLE:       Indexed retrieval cannot be chosen if a stored procedure is used inside the comparison predicate
DESCRIPTION:
JIRA:        CORE-2132
"""

import pytest
from firebird.qa import *

init_script = """create table t1 (col int primary key);
set term ^ ;
create procedure p1 returns (ret int) as begin ret = 0; suspend; end ^
create procedure p2 (prm int) returns (ret int) as begin ret = prm; suspend; end ^
set term ; ^
commit;
insert into t1 (col) values (0);
commit;
"""

db = db_factory(init=init_script)

test_script = """set plan on ;

-- index
select * from t1 where col = 0;
-- natural
select * from t1 where col = col;
-- index
select * from t1 where col = ( select 0 from rdb$database );
-- natural
select * from t1 where col = ( select col from rdb$database );
-- index (currently natural)
select * from t1 where col = ( select 0 from p1 );
-- index (currently natural)
select * from t1 where col = ( select ret from p1 );
-- natural
select * from t1 where col = ( select col from p1 );
-- index (currently natural)
select * from t1 where col = ( select 0 from p2(0) );
-- index (currently natural)
select * from t1 where col = ( select ret from p2(0) );
-- natural
select * from t1 where col = ( select col from p2(0) );
-- natural
select * from t1 where col = ( select 0 from p2(col) );
-- natural
select * from t1 where col = ( select ret from p2(col) );
-- natural
select * from t1 where col = ( select col from p2(col) );

"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (T1 INDEX (RDB$PRIMARY1))

         COL
============
           0


PLAN (T1 NATURAL)

         COL
============
           0


PLAN (RDB$DATABASE NATURAL)
PLAN (T1 INDEX (RDB$PRIMARY1))

         COL
============
           0


PLAN (RDB$DATABASE NATURAL)
PLAN (T1 NATURAL)

         COL
============
           0


PLAN (P1 NATURAL)
PLAN (T1 INDEX (RDB$PRIMARY1))

         COL
============
           0


PLAN (P1 NATURAL)
PLAN (T1 INDEX (RDB$PRIMARY1))

         COL
============
           0


PLAN (P1 NATURAL)
PLAN (T1 NATURAL)

         COL
============
           0


PLAN (P2 NATURAL)
PLAN (T1 INDEX (RDB$PRIMARY1))

         COL
============
           0


PLAN (P2 NATURAL)
PLAN (T1 INDEX (RDB$PRIMARY1))

         COL
============
           0


PLAN (P2 NATURAL)
PLAN (T1 NATURAL)

         COL
============
           0


PLAN (P2 NATURAL)
PLAN (T1 NATURAL)

         COL
============
           0


PLAN (P2 NATURAL)
PLAN (T1 NATURAL)

         COL
============
           0


PLAN (P2 NATURAL)
PLAN (T1 NATURAL)

         COL
============
           0

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

