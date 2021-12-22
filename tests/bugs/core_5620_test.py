#coding:utf-8
#
# id:           bugs.core_5620
# title:        Add builtin functions FIRST_DAY and LAST_DAY
# decription:   
#                  Checked on:  4.0.0.783: OK, 0.781s.
#                
# tracker_id:   CORE-5620
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
    select
         first_day(of month from date '2017-09-15') -- 2017-09-01
        ,first_day(of year from date '2017-09-15') -- 2017-01-01
        ,first_day(of week from timestamp '2017-11-01 12:13:14.5678') -- 2017-10-29 12:13:14.5678
        ,last_day(of month from date '2017-09-15') -- 2017-09-30
        ,last_day(of year from date '2017-09-15') -- 2017-12-31
        ,last_day(of week from timestamp '2017-11-01 12:13:14.5678') -- 2017-11-04 12:13:14.5678 
    from rdb$database;

    select
         last_day(of month from date '2000-02-05') -- 2000.02.29
        ,last_day(of month from date '2001-02-05') -- 2001.02.28
        ,last_day(of month from date '2004-02-05') -- 2004.02.29
        ,last_day(of month from date '2100-02-05') -- 2100.02.28
    from rdb$database;


    select
          last_day(of week from date '2008-12-28') -- 2009.01.03
         ,first_day(of week from date '2009-01-03') -- 2008.12.28
    from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    FIRST_DAY                       2017-09-01
    FIRST_DAY                       2017-01-01
    FIRST_DAY                       2017-10-29 12:13:14.5678
    LAST_DAY                        2017-09-30
    LAST_DAY                        2017-12-31
    LAST_DAY                        2017-11-04 12:13:14.5678
    LAST_DAY                        2000-02-29
    LAST_DAY                        2001-02-28
    LAST_DAY                        2004-02-29
    LAST_DAY                        2100-02-28
    LAST_DAY                        2009-01-03
    FIRST_DAY                       2008-12-28
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

