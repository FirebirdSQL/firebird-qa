#coding:utf-8

"""
ID:          issue-1457
ISSUE:       1457
TITLE:       Wrong single-segment ascending index on character field with NULL and empty string values
DESCRIPTION:
JIRA:        CORE-1040
"""

import pytest
from firebird.qa import *

init_script = """recreate table t (str varchar(10));
commit;

insert into t values ('');
insert into t values (null);
commit;

create index t_i on t (str);
commit;
"""

db = db_factory(init=init_script)

test_script = """select count(*) from t where str is null;"""

act = isql_act('db', test_script)

expected_stdout = """                COUNT
=====================
                    1

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

