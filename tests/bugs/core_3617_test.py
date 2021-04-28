#coding:utf-8
#
# id:           bugs.core_3617
# title:        Window Function: cume_dist()
# decription:   Could not find any interesting sample with this function. Decided to use string comparison with unicode_ci_ai collation.
# tracker_id:   CORE-3617
# min_versions: []
# versions:     4.0
# qmid:         bugs.core_3617

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create domain dm_utf8 varchar(20) character set utf8 collate unicode_ci_ai;
    commit;
    recreate table test_ciai( id int, s dm_utf8 );
    commit;

    insert into test_ciai values(1, 'CANción');
    insert into test_ciai values(2, 'peluqueria');
    insert into test_ciai values(3, 'peluQUEría');
    insert into test_ciai values(4, 'cancíON');
    commit;

    set list on;

    select s, id, cume_dist()over(order by s) as c_dist
    from test_ciai
    order by cume_dist()over(order by id desc);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    S                               cancíON
    ID                              4
    C_DIST                          0.5000000000000000
    
    S                               peluQUEría
    ID                              3
    C_DIST                          1.000000000000000

    S                               peluqueria
    ID                              2
    C_DIST                          1.000000000000000

    S                               CANción
    ID                              1
    C_DIST                          0.5000000000000000
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

