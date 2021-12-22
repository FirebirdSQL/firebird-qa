#coding:utf-8
#
# id:           bugs.core_4299
# title:        Inappropriate self-reference of column when using "with check option" with extract(...)
# decription:   
# tracker_id:   CORE-4299
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """
    -- Source description found here:
    -- http://stackoverflow.com/questions/20505769/inappropriate-self-reference-of-column-when-using-with-check-option-in-fireb
    create or alter view foo as select current_date dt from rdb$database;
    commit;
    
    recreate table bar(dt date);
    commit;
    insert into bar(dt) values ('28.03.2011');
    commit;
    
    create or alter view foo as
    select * from bar
    where extract(year from bar.dt) = '2011' 
    with check option
    ; 
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
  set list on;
  select * from foo;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  DT                              2011-03-28
"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

