#coding:utf-8
#
# id:           bugs.core_1146
# title:        AV in rse\\invalidate_child_rpbs for recursive queies
# decription:   This may crash the server with AV
# tracker_id:   CORE-1146
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1146

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table c (
      id integer,
      name varchar(100)
    );
    recreate table t (
      id integer,
      ownercode integer,
      code integer
    );
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Updated code to recent FB version: add prefixes to every field from the query
    with recursive x as
    (
      select --1 as step,
             t.id, t.ownercode, t.code, c2.name as ownclass, c1.name as class
        from t inner join c c1 on c1.id = t.code
               left join c c2 on c2.id = t.ownercode
        where ownercode = 0
    
      union all
    
      select --x.step+1
             t.id, t.ownercode, x.code, c2.name as ownclass, c1.name as class
        from t inner join c c1 on c1.id = t.code
               left join c c2 on c2.id = t.ownercode
               inner join x on t.ownercode = x.code
    )
    select * from x
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1')
def test_core_1146_1(act_1: Action):
    act_1.execute()

