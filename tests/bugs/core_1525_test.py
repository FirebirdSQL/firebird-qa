#coding:utf-8
#
# id:           bugs.core_1525
# title:        Computed field + index not working in WHERE
# decription:   
# tracker_id:   
# min_versions: ['2.0.7']
# versions:     2.0.7
# qmid:         bugs.core_1525

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table test_1 (
      id integer not null,
      last_day date,
      comp_last_day computed by (coalesce(last_day, cast('2999-12-31' as date)))
    );
    
     
    insert into test_1 values (1, '2007-10-10');
    insert into test_1 values (2, null);
    commit;
    
    set list on;

    select *
    from test_1
    where cast ('2007-09-09' as date) < comp_last_day;

    create index idx_1 on test_1 computed by ( coalesce(last_day, cast('2999-12-31' as date)) );
    commit;
    set plan on;

    select *
    from test_1
    where cast ('2007-09-09' as date) < comp_last_day;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    LAST_DAY                        2007-10-10
    COMP_LAST_DAY                   2007-10-10
    ID                              2
    LAST_DAY                        <null>
    COMP_LAST_DAY                   2999-12-31
    
    PLAN (TEST_1 INDEX (IDX_1))
    
    ID                              1
    LAST_DAY                        2007-10-10
    COMP_LAST_DAY                   2007-10-10
    ID                              2
    LAST_DAY                        <null>
    COMP_LAST_DAY                   2999-12-31
  """

@pytest.mark.version('>=2.0.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

