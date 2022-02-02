#coding:utf-8

"""
ID:          issue-1417
ISSUE:       1417
TITLE:       AV at rollback and \\ or garbage collection if updated table have expression index with SELECT in it
DESCRIPTION:
JIRA:        CORE-1006
FBTEST:      bugs.core_1006
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup='core1006.fbk')

test_script = """
    set term ^;
    execute block
    as
        declare f1 int;
        declare f2 int;
    begin
        for
            select
                t1.id
                    as id1 -- <<< ::: NB ::: add alias, otherwise can`t compile in 3.0
                ,t2.id
                    as id2 -- <<< ::: NB ::: add alias, otherwise can`t compile in 3.0
            from table1 t1, table2 t2
            where t1.id = t2.id
            into :f1, :f2
            as cursor cur
        do
            update table1 set name = :f1 + :f2 where current of cur;
    end
    ^ set term ;^
    rollback;
"""

act = isql_act('db', test_script)

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.execute()
