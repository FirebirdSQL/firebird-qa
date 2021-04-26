#coding:utf-8
#
# id:           bugs.core_2132
# title:        Indexed retrieval cannot be chosen if a stored procedure is used inside the comparison predicate
# decription:   
# tracker_id:   CORE-2132
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t1 (col int primary key);
set term ^ ;
create procedure p1 returns (ret int) as begin ret = 0; suspend; end ^
create procedure p2 (prm int) returns (ret int) as begin ret = prm; suspend; end ^
set term ; ^
commit;
insert into t1 (col) values (0);
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set plan on ;

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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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

@pytest.mark.version('>=2.5.0')
def test_core_2132_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

