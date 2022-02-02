#coding:utf-8

"""
ID:          issue-5498
ISSUE:       5498
TITLE:       Explicitly defined names for NOT NULL constraints are not exported into script by ISQL -x
DESCRIPTION:
JIRA:        CORE-5218
FBTEST:      bugs.core_5218
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table test(
       f01 int constraint f01_nn not null constraint f01_pk primary key
      ,f02 int constraint f02_nn not null constraint f02_uk unique
      -- NB: 3.0 allows to skip reference of PK column from table that
      --- is created now, i.e. one may to declare FK-field like this:
      -- ... f03 references test
      -- That's not so for 2.5.x:
      ,f03 int constraint f03_nn not null
       constraint f03_fk
       references test( f01 )
       --                ^-- this must be specified in 2.5.x
    );
"""

db = db_factory(init=init_script)

act = python_act('db')

expected_stdout = """
    CREATE TABLE TEST (F01 INTEGER CONSTRAINT F01_NN NOT NULL,
            F02 INTEGER CONSTRAINT F02_NN NOT NULL,
            F03 INTEGER CONSTRAINT F03_NN NOT NULL,
    CONSTRAINT F01_PK PRIMARY KEY (F01),
    CONSTRAINT F02_UK UNIQUE (F02));
    ALTER TABLE TEST ADD CONSTRAINT F03_FK FOREIGN KEY (F03) REFERENCES TEST (F01);
"""

@pytest.mark.version('>=2.5.6')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.isql(switches=['-x'])
    # filter stdout
    act.stdout = '\n'.join([line for line in act.stdout.splitlines() if 'CONSTRAINT' in line])
    assert act.clean_stdout == act.clean_expected_stdout


