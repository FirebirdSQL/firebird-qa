#coding:utf-8
#
# id:           bugs.core_1006
# title:        AV at rollback and \\ or garbage collection if updated table have expression index with SELECT in it
# decription:   This test takes the server down.
# tracker_id:   CORE-1006
# min_versions: []
# versions:     2.0.1
# qmid:         bugs.core_1006

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core1006.fbk', init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.0.1')
def test_1(act_1: Action):
    act_1.execute()

