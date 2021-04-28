#coding:utf-8
#
# id:           bugs.core_3090
# title:        Incorrect LEFT JOIN result using table and derived constant subquery
# decription:   
# tracker_id:   CORE-3090
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """recreate table test_err (id int);
insert into test_err (ID) values (1);
insert into test_err (ID) values (2);
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select *
  from test_err t
       left join (select 1 id from rdb$database) a on a.id = t.id;
select
  RESULT
from (select
    'Well' as RESULT
  from (select
      (select 'Does not work' from RDB$DATABASE) as D
    from RDB$DATABASE d) i
  left join RDB$DATABASE on 1=0) j
left join RDB$DATABASE on 1=0;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID           ID
============ ============
           1            1
           2       <null>


RESULT
======
Well

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

