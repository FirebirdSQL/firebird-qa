#coding:utf-8

"""
ID:          issue-5402
ISSUE:       5402
TITLE:       Indices on computed fields are broken after restore (all keys are NULL)
DESCRIPTION:
JIRA:        CORE-5118
FBTEST:      bugs.core_5118
NOTES:
    [12.09.2024] pzotov
    Replaced test query so that it does not use index navigation ('plan order') but still checks indexed access.
    Three separate queries with 'PLAN ... INDEX' are used instead of one with 'where <comp_field> IN <literals_list>'.
    This is because of optimizer changed in 5.x and issues plan with only *one* occurrence of 'INDEX' for such cases.
    See: https://github.com/FirebirdSQL/firebird/pull/7707 - "Better processing and optimization if IN <list>".
    Commit: https://github.com/FirebirdSQL/firebird/commit/0493422c9f729e27be0112ab60f77e753fabcb5b, 04-sep-2023.

    Requested by dimitr, letters with subj 'core_5118_test', since 11.09.2024 17:26.

    Checked on 6.0.0.452, 5.0.2.1493, 4.0.5.3136, 3.0.13.33789
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

db = db_factory(init = init_script)

act = python_act('db', substitutions = [ ('[ \t]+',' ') ])

expected_stdout = """
    PLAN (TEST INDEX (TEST_CONCAT_TEXT))
    CONCAT_TEXT nom1 prenom1
    Records affected: 1

    PLAN (TEST INDEX (TEST_CONCAT_TEXT))
    CONCAT_TEXT nom2 prenom2
    Records affected: 1

    PLAN (TEST INDEX (TEST_CONCAT_TEXT))
    CONCAT_TEXT nom3 prenom3
    Records affected: 1
"""

test_sql = """
    set list on;
    set plan on;
    set count on;
    select concat_text from test where concat_text = 'nom1 prenom1';
    select concat_text from test where concat_text = 'nom2 prenom2';
    select concat_text from test where concat_text = 'nom3 prenom3';
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    with act.connect_server() as srv:
        backup = BytesIO()
        srv.database.local_backup(database = act.db.db_path, backup_stream = backup)
        backup.seek(0)
        srv.database.local_restore(database = act.db.db_path, backup_stream=backup, flags = SrvRestoreFlag.REPLACE)
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input = test_sql, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
