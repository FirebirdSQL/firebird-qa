# coding:utf-8

"""
ID:          functional.tablespace.primary_ts
TITLE:       Test PRIMARY TS.
DESCRIPTION: 
"""

import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('===*', '==============='),
                 ('FILE .*test.fdb', 'FILE TEST.FDB'),
                 ('FILE .*TEST.FDB', 'FILE TEST.FDB')]

act = python_act('db', substitutions=substitutions)

expected_output = """
RESULT_1
===============
1
RESULT_2
===============
1
RESULT_3
===============
616
RESULT_4
===============
0
RESULT_5
===============
"PRIMARY" ONLINE READ WRITE
RESULT_6
===============
105
RESULT_7
===============
0
RESULT_8
===============
42
RESULT_9
===============
0
RESULT_10
===============
<null>
RESULT_11
===============
<null>
RESULT_12
===============
<null>
RESULT_14
===============
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-ALTER TABLESPACE PRIMARY failed
-Cannot ALTER or DROP system tablespace PRIMARY
RESULT_15
===============
Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-DROP TABLESPACE PRIMARY failed
-Cannot ALTER or DROP system tablespace PRIMARY
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action):

    test_script = f"""
    create tablespace ts file 'test.dat';
    create table test(id int primary key) tablespace primary;
    create index t_in on test(id) tablespace primary;
    commit;

    SELECT COUNT(*) AS RESULT_1 FROM RDB$TABLESPACES WHERE RDB$TABLESPACE_NAME = 'PRIMARY';
    SELECT COUNT(*) AS RESULT_2 FROM RDB$TABLESPACES WHERE RDB$TABLESPACE_NAME != 'PRIMARY';

    SELECT COUNT(*) AS RESULT_3 FROM RDB$RELATION_FIELDS WHERE RDB$TABLESPACE_NAME = 'PRIMARY';
    SELECT COUNT(*) AS RESULT_4 FROM RDB$RELATION_FIELDS WHERE RDB$TABLESPACE_NAME != 'PRIMARY';

    select '' as result_5 from rdb$database;
    SHOW TABLESPACE PRIMARY;

    SELECT COUNT(*) AS RESULT_6 FROM RDB$INDICES WHERE RDB$TABLESPACE_NAME = 'PRIMARY';
    SELECT COUNT(*) AS RESULT_7 FROM RDB$INDICES WHERE RDB$TABLESPACE_NAME != 'PRIMARY';

    SELECT COUNT(*) AS RESULT_8 FROM RDB$RELATIONS WHERE RDB$TABLESPACE_NAME = 'PRIMARY';
    SELECT COUNT(*) AS RESULT_9 FROM RDB$RELATIONS WHERE RDB$TABLESPACE_NAME != 'PRIMARY';

    CREATE VIEW VIEW_TEST AS SELECT * FROM TEST;
    COMMIT;
    SELECT RDB$TABLESPACE_NAME AS RESULT_10 FROM RDB$RELATIONS WHERE RDB$RELATION_NAME = 'VIEW_TEST';

    CREATE GLOBAL TEMPORARY TABLE gtt_test (id INT);
    COMMIT;
    SELECT RDB$TABLESPACE_NAME AS RESULT_11 FROM RDB$RELATIONS WHERE RDB$RELATION_NAME = 'GTT_TEST';

    CREATE TABLE ext_test external FILE 'test.tbl' (id int);
    COMMIT;
    SELECT RDB$TABLESPACE_NAME AS RESULT_12 FROM RDB$RELATIONS WHERE RDB$RELATION_NAME = 'EXT_TEST';

    select '' as RESULT_14 from rdb$database;
    ALTER TABLESPACE PRIMARY SET FILE 'test.dat';
    select '' as RESULT_15 from rdb$database;
    DROP TABLESPACE PRIMARY;
    """
    act.isql(switches=['-q'], input=test_script, combine_output=True)

    act.expected_stdout = expected_output
    assert act.clean_stdout == act.clean_expected_stdout
