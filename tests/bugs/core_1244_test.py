#coding:utf-8
#
# id:           bugs.core_1244
# title:        Server crash on select * from <recursive CTE>
# decription:   Simple select from recursive CTE crashes the server when query uses asterisk.
# tracker_id:   CORE-1244
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1244

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE ARTICLES (ARTICLEID integer, PARENTID integer);
COMMIT;
INSERT INTO ARTICLES VALUES (1,NULL);
INSERT INTO ARTICLES VALUES (2,1);
COMMIT;"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """with recursive
    Art_Tree as (
        select A.ArticleID
          from Articles A
         where A.ParentID is NULL

union all

select A.ArticleID
          from Articles A
               join Art_Tree T on (A.ParentID=T.ArticleID)
    )
select *
  from Art_Tree;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ARTICLEID
============
           1
           2

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

