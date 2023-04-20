#coding:utf-8

"""
ID:          issue-7001
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7001
TITLE:       ISQL showing publication status
DESCRIPTION:
NOTES:
    [20.04.2023] pzotov
    command 'show pub;' currently displays "There is no publications in this database".
    This is expected. Detailed output of this command will be implemented later (discussed with dimitr).
    Checked on 5.0.0.1022 (intermediate build)
"""
import locale
import pytest
from firebird.qa import *

# QA_GLOBALS -- dict, is defined in qa/plugin.py, obtain settings
# from act.files_dir/'test_config.ini':
repl_settings = QA_GLOBALS['replication']

MAIN_DB_ALIAS = repl_settings['main_db_alias']

db_main = db_factory( filename = '#' + MAIN_DB_ALIAS, do_not_create = True, do_not_drop = True)

substitutions = [('^((?!(Publication:|RDB\\$DEFAULT)).)*$', ''),]

act_db_main = python_act('db_main', substitutions = substitutions)

#--------------------------------------------

@pytest.mark.version('>=5.0')
def test_1(act_db_main: Action, capsys):
    test_sql = """
        show database;
        show sys pub;
        show pub rdb$default;
    """

    act_db_main.expected_stdout = """
        Publication: Enabled
        RDB$DEFAULT
        RDB$DEFAULT: Enabled, Auto-enable
    """
    act_db_main.isql(switches=['-q', '-nod'], input = test_sql, combine_output = True, io_enc = locale.getpreferredencoding())
    assert act_db_main.clean_stdout == act_db_main.clean_expected_stdout
