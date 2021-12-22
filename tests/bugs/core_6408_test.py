#coding:utf-8
#
# id:           bugs.core_6408
# title:        RETURNING clause in MERGE cannot reference column in aliased target table using qualified reference (alias.column) if DELETE action present
# decription:   
#                  Confirmed problem on 4.0.0.2225 ("-SQL error code = -206 / -Column unknown / -D.VAL"
#                  Checked on 4.0.0.2240 - all fine.
#                
# tracker_id:   CORE-6408
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    recreate table dummy2 (
      id integer constraint pk_dummy2 primary key,
      val varchar(50)
    );
    commit;
    insert into dummy2 (id) values (1);
    commit;

    merge into dummy2 as d
      using (select 1, 'ab' from rdb$database) as src(id, val)
      on d.id = src.id
      when matched and d.id = 2 then delete
      when matched then update set d.val = src.val
      returning
           d.val ----  this was not allowed before fix ("Statement failed, SQLSTATE = 42S22 ... Column unknown")
          ,new.val
          ,old.val
          ,src.val
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    VAL                             ab
    CONSTANT                        ab
    VAL                             <null>
    VAL                             ab
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

