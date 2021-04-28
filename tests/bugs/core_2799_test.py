#coding:utf-8
#
# id:           bugs.core_2799
# title:        Changing sort directon in delete statement cause deletion of all records in table
# decription:   
#                  Checked on: 
#                      WI-T3.0.0.31374 Firebird 3.0 Beta 1
#                      WI-V3.0.0.32300 Firebird 3.0 Release Candidate 2
#                
# tracker_id:   CORE-2799
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test
    (
        id integer not null primary key,
        kod varchar(5)
    );
    commit;

    insert into test(id, kod) values(1, 'abc');
    insert into test(id, kod) values(2, 'abc');
    commit;
    
    -- now we have 2 rows in table
    -- and delete in ___ascending___ oreder

    set count on;
    --set echo on;

    delete from test t 
    where exists(select * from test t2 where t2.id<>t.id and t2.kod=t.kod) 
    order by t.id asc;
    -- 2.5: one row affected
    -- 3.0: TWO rows must be affected.
    commit;
    
    
    select * from test;
    -- 2.5: one row selected id=2 kod='abc'
    -- 3.0: NO rows should be selected here.
    
    set count off;
    delete from test;
    commit;
    insert into test(id, kod) values(1, 'abc');
    insert into test(id, kod) values(2, 'abc');
    commit;
    set count on;

    -- now we have 2 rows in table
    -- and delete in ___descending___ oreder
    
    delete from test t 
    where exists(select * from test t2 where t2.id<>t.id and t2.kod=t.kod) 
    order by t.id desc;
    -- 2.5: two rows affected.
    -- 3.0: TWO rows must be affected.
    commit;

    select * from test;
    -- 2.5: empty result set.
    -- 3.0: NO rows should be selected here.

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 2
    Records affected: 0
    Records affected: 2
    Records affected: 0
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

