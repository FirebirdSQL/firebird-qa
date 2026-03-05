#coding:utf-8

"""
ID:          issue-2325
ISSUE:       2325
TITLE:       Circular dependencies between computed fields crash the engine
DESCRIPTION:
JIRA:        CORE-1894
FBTEST:      bugs.core_1894
NOTES:
    [26.06.2025] pzotov
    Separated expected output for FB major versions prior/since 6.x.
    No substitutions are used to suppress schema and quotes. Discussed with dimitr, 24.06.2025 12:39.
    Checked on 6.0.0.876; 5.0.3.1668; 4.0.6.3214; 3.0.13.33813.
    [05.03.2026] pzotov
    Adjusted expected output which has changed since #b38046e1 ('Encapsulation of metadata cache'; 24-feb-2026 17:31:04 +0000).
    Checked on 6.0.0.1807-46797ab.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table t (
        n integer,
        n1 computed by (n),
        n2 computed by (n1)
    );

    recreate table t2 (
        n integer,
        c1 computed by (1),
        c2 computed by (c1)
    );

    alter table t alter n1 computed by (n2);
    commit;

    set autoddl off;
    alter table t2 drop c1;
    alter table t2 add c1 computed by (c2);
    commit;

    select * from t;
    select * from t2; -- THIS LEAD SERVER CRASH (checked on WI-T4.0.0.399)
"""

act = isql_act('db', test_script)

expected_stdout_5x = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -Cannot have circular dependencies with computed fields

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN T2.C1
    -there are 1 dependencies

    Statement failed, SQLSTATE = 42000
    Cannot have circular dependencies with computed fields

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN T2.C1
    -there are 1 dependencies
"""

expected_stdout_6x = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -Cannot have circular dependencies with computed fields
    
    Statement failed, SQLSTATE = 42S22
    unsuccessful metadata update
    -ALTER TABLE "PUBLIC"."T2" failed
    -invalid request BLR at offset 5
    -column "C1" is not defined in table "PUBLIC"."T2"
    
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN "PUBLIC"."T2"."C1"
    -there are 1 dependencies
    
    Statement failed, SQLSTATE = 42S22
    invalid request BLR at offset 5
    -column "C1" is not defined in table "PUBLIC"."T2"
    
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN "PUBLIC"."T2"."C1"
    -there are 1 dependencies
"""

@pytest.mark.version('>=3.0.2')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
