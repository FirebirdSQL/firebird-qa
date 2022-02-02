#coding:utf-8

"""
ID:          issue-5402
ISSUE:       5402
TITLE:       Indices on computed fields are broken after restore (all keys are NULL)
DESCRIPTION:
JIRA:        CORE-5118
FBTEST:      bugs.core_5118
"""

import pytest
from io import BytesIO
from firebird.qa import *
from firebird.driver import SrvRestoreFlag

init_script = """
    recreate table test (
        id int,
        x varchar(10),
        y varchar(10) ,
        concat_text computed by (x || ' ' || y)
    );
    commit;

    insert into test(id, x, y) values (1, 'nom1', 'prenom1');
    insert into test(id, x, y) values (2, 'nom2', 'prenom2');
    insert into test(id, x, y) values (3, 'nom3', 'prenom3');
    commit;

    create index test_concat_text on test computed by ( concat_text );
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db')

expected_stdout = """
    PLAN (TEST ORDER TEST_CONCAT_TEXT)

    ID                              1
    X                               nom1
    Y                               prenom1
    CONCAT_TEXT                     nom1 prenom1

    ID                              2
    X                               nom2
    Y                               prenom2
    CONCAT_TEXT                     nom2 prenom2

    ID                              3
    X                               nom3
    Y                               prenom3
    CONCAT_TEXT                     nom3 prenom3

    Records affected: 3
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    with act.connect_server() as srv:
        backup = BytesIO()
        srv.database.local_backup(database=act.db.db_path, backup_stream=backup)
        backup.seek(0)
        srv.database.local_restore(database=act.db.db_path, backup_stream=backup,
                                   flags=SrvRestoreFlag.REPLACE)
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'],
               input='set list on; set plan on; set count on; select * from test order by concat_text;')
    assert act.clean_stdout == act.clean_expected_stdout
