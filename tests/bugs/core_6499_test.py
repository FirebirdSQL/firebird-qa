#coding:utf-8

"""
ID:          issue-6729
ISSUE:       6729
TITLE:       Regression: gstat with switch -t executed via services fails with "found unknown switch" error
DESCRIPTION:
  Test creates several tables and request statistics for one of them usin Services API.
  Output must contain for one and only one (selected) table - TEST_01 (and its index).
  All lines from output which do not include this name are ignored (see 'subst' section).
JIRA:        CORE-6499
FBTEST:      bugs.core_6499
"""

import pytest
from firebird.qa import *
from firebird.driver import SrvStatFlag

substitutions = [('^((?!TEST_01\\s+\\(|TEST_01_ID\\s+\\().)*$', ''),
                 ('TEST_01\\s+\\(.*', 'TEST_01'),
                 ('Index TEST_01_ID\\s+\\(.*', 'Index TEST_01_ID'), ('[ \t]+', ' ')]

init_script = """
    recreate table test_01(id int);
    recreate table test__01(id int);
    recreate table test__011(id int);
    commit;
    insert into test_01 select row_number()over() from rdb$types;
    commit;
    create index test_01_id on test_01(id);
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db', substitutions=substitutions)

expected_stdout = """
    TEST_01 (128)
    Index TEST_01_ID (0)
"""

@pytest.mark.version('>=3.0.8')
def test_1(act: Action, capsys):
    with act.connect_server() as srv:
        srv.database.get_statistics(database=act.db.db_path, tables=['TEST_01'],
                                    flags=SrvStatFlag.DATA_PAGES | SrvStatFlag.IDX_PAGES,
                                    callback=act.print_callback)
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
