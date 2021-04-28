#coding:utf-8
#
# id:           bugs.core_0037
# title:        Navigation vs IS NULL vs compound index
# decription:   
#                   24.01.2019. Added separate code for running on FB 4.0+.
#                   UDF usage is deprecated in FB 4+, see: ".../doc/README.incompatibilities.3to4.txt".
#                   Functions div, frac, dow, sdow, getExactTimestampUTC and isLeapYear got safe replacement 
#                   in UDR library "udf_compat", see it in folder: ../plugins/udr/
#                   Checked on:
#                       2.5.9.27126: OK, 0.656s.
#                       3.0.5.33086: OK, 1.422s.
#                       4.0.0.1172: OK, 4.109s.
#                       4.0.0.1340: OK, 2.297s.
#                       4.0.0.1378: OK, 2.204s.    
#                
# tracker_id:   CORE-0037
# min_versions: ['2.5.0']
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
    set bail on;

    -- See declaration sample in plugins\\udr\\UdfBackwardCompatibility.sql:

    create function UDR40_frac (
        val double precision
    ) returns double precision
    external name 'udf_compat!UC_frac'
    engine udr;

    recreate view v1 as select 1 k from rdb$database;
    recreate view v2 as select 1 k from rdb$database;
    commit;

    recreate table t1
    (
      t1f1 integer not null primary key,
      t1f2 varchar(30)
    );

    recreate table t2
    (
      t2f1 integer not null primary key,
      t2f2 integer not null,
      t2f3 varchar(30)
    );

    create index t2f2_ndx on t2(t2f2);

    recreate view v1 as select * from t1 where UDR40_frac( mod(t1f1,100) / 100.000) > 0.03;
    recreate view v2 as select * from t2 where UDR40_frac( mod(t2f1,100) / 100.000) > 0.03;

    insert into t1(t1f1, t1f2) values (1, '1');
    insert into t1(t1f1, t1f2) values (2, '2');
    insert into t1(t1f1, t1f2) values (3, '3');
    insert into t1(t1f1, t1f2) values (104, '104');
    insert into t1(t1f1, t1f2) values (105, '205');
    insert into t1(t1f1, t1f2) values (106, '106');

    insert into t2(t2f1, t2f2, t2f3) values (1, 1, '1');
    insert into t2(t2f1, t2f2, t2f3) values (2, 2, '2');
    insert into t2(t2f1, t2f2, t2f3) values (3, 3, '3');
    insert into t2(t2f1, t2f2, t2f3) values (104, 104, '104');
    insert into t2(t2f1, t2f2, t2f3) values (105, 105, '105');
    insert into t2(t2f1, t2f2, t2f3) values (106, 106, '106');

    set count on;

    select x.*, y.*, UDR40_frac( mod(t2f1,100) / 100.000)
    from v1 x, v2 y
    where x.t1f1 = y.t2f2 
    and UDR40_frac( mod(t2f1,100) / 100.000) < 0.03
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

