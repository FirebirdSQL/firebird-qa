#coding:utf-8

"""
ID:          issue-7675
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7675
TITLE:       EXPLAIN statement and RDB$SQL package
DESCRIPTION:
    Test only ckecks ability to use RDB$SQL package as it is described in the doc.
    More complex tests will be implemented later.
NOTES:
    [02.10.2023] pzotov
    Checked on 6.0.0.65.
"""

import pytest
from firebird.qa import *

init_sql = """
    recreate table tdetl(id int primary key);
    recreate table tmain(id int primary key using index tmain_pk, x int);
    recreate table tdetl(id int primary key using index tdetl_pk, pid int references tmain using index tdetl_fk, y int, z int);
    commit;

    insert into tmain(id,x) select row_number()over(), -100 + rand()*200 from rdb$types rows 100;
    insert into tdetl(id, pid, y,z) select row_number()over(), 1+rand()*99, rand()*1000, rand()*1000 from rdb$types;
    commit;

    create index tmain_x on tmain(x);
    create index tdetl_y on tdetl(y);
    create index tdetl_z on tdetl(z);

    set statistics index tdetl_fk;
    commit;
"""
db = db_factory(init = init_sql)

test_script = """
    set list on;
    select *
    from rdb$sql.explain(
        q'{
            select m2.id, count(*)
            from tmain m2
            join tdetl d using(id)
            where m2.x > 0
            group by 1
          }'
    ) p
    order by p.plan_line;
"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN_LINE                       1
    RECORD_SOURCE_ID                7
    PARENT_RECORD_SOURCE_ID         <null>
    LEVEL                           0
    OBJECT_TYPE                     <null>
    PACKAGE_NAME                    <null>
    OBJECT_NAME                     <null>
    ALIAS                           <null>
    CARDINALITY                     <null>
    RECORD_LENGTH                   <null>
    KEY_LENGTH                      <null>
    ACCESS_PATH                     0:4
    Select Expression
    PLAN_LINE                       2
    RECORD_SOURCE_ID                6
    PARENT_RECORD_SOURCE_ID         7
    LEVEL                           1
    OBJECT_TYPE                     <null>
    PACKAGE_NAME                    <null>
    OBJECT_NAME                     <null>
    ALIAS                           <null>
    CARDINALITY                     0.1000000000000000
    RECORD_LENGTH                   <null>
    KEY_LENGTH                      <null>
    ACCESS_PATH                     0:5
    -> Aggregate
    PLAN_LINE                       3
    RECORD_SOURCE_ID                5
    PARENT_RECORD_SOURCE_ID         6
    LEVEL                           2
    OBJECT_TYPE                     <null>
    PACKAGE_NAME                    <null>
    OBJECT_NAME                     <null>
    ALIAS                           <null>
    CARDINALITY                     100.0000000000000
    RECORD_LENGTH                   <null>
    KEY_LENGTH                      <null>
    ACCESS_PATH                     0:6
    -> Nested Loop Join (inner)
    PLAN_LINE                       4
    RECORD_SOURCE_ID                2
    PARENT_RECORD_SOURCE_ID         5
    LEVEL                           3
    OBJECT_TYPE                     <null>
    PACKAGE_NAME                    <null>
    OBJECT_NAME                     <null>
    ALIAS                           <null>
    CARDINALITY                     100.0000000000000
    RECORD_LENGTH                   <null>
    KEY_LENGTH                      <null>
    ACCESS_PATH                     0:7
    -> Filter
    PLAN_LINE                       5
    RECORD_SOURCE_ID                1
    PARENT_RECORD_SOURCE_ID         2
    LEVEL                           4
    OBJECT_TYPE                     0
    PACKAGE_NAME                    <null>
    OBJECT_NAME                     TMAIN
    ALIAS                           M2
    CARDINALITY                     100.0000000000000
    RECORD_LENGTH                   <null>
    KEY_LENGTH                      <null>
    ACCESS_PATH                     0:8
    -> Table "TMAIN" as "M2" Access By ID
    -> Index "TMAIN_PK" Full Scan
    -> Bitmap
    -> Index "TMAIN_X" Range Scan (lower bound: 1/1)
    PLAN_LINE                       6
    RECORD_SOURCE_ID                4
    PARENT_RECORD_SOURCE_ID         5
    LEVEL                           3
    OBJECT_TYPE                     <null>
    PACKAGE_NAME                    <null>
    OBJECT_NAME                     <null>
    ALIAS                           <null>
    CARDINALITY                     1.000000000000000
    RECORD_LENGTH                   <null>
    KEY_LENGTH                      <null>
    ACCESS_PATH                     0:9
    -> Filter
    PLAN_LINE                       7
    RECORD_SOURCE_ID                3
    PARENT_RECORD_SOURCE_ID         4
    LEVEL                           4
    OBJECT_TYPE                     0
    PACKAGE_NAME                    <null>
    OBJECT_NAME                     TDETL
    ALIAS                           D
    CARDINALITY                     0.9999999999999999
    RECORD_LENGTH                   <null>
    KEY_LENGTH                      <null>
    ACCESS_PATH                     0:a
    -> Table "TDETL" as "D" Access By ID
    -> Bitmap
    -> Index "TDETL_PK" Unique Scan
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
