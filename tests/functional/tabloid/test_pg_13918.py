#coding:utf-8
#
# id:           functional.tabloid.pg_13918
# title:        Some _TRIVIAL_ queries allow to specify HAVING without group by, and for such case one may to get record from EMPTY source rowset(!)
# decription:   
#                  Original issue:
#                  http://www.postgresql.org/message-id/flat/CAKFQuwYSa5Dzvw8KdxhiUAY+fjbO4DRQ-sDqQXPVexvVoTkvQA@mail.gmail.com#CAKFQuwYSa5Dzvw8KdxhiUAY+fjbO4DRQ-sDqQXPVexvVoTkvQA@mail.gmail.com
#               
#                  See also http://www.postgresql.org/docs/9.5/interactive/sql-select.html
#                  ===
#                    The presence of HAVING turns a query into a grouped query even if there is no GROUP BY clause <...>
#                    Such a query will emit a single row if the HAVING condition is true, zero rows if it is not true.
#                  ===
#               
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on; 
    -- This compiles OK and, moreover, outputs one record:
    select 123456789 as "Yeah!" from rdb$database where 1=0 having 1=1;
    select 987654321 as "Waw!!" from rdb$database where 1=0 having 1=2;

    -- Following will NOT compile:
    -- select i from (select 1 i from rdb$database) where i<0 having 1=0;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Yeah!                           123456789
    Records affected: 1
    Records affected: 0
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

