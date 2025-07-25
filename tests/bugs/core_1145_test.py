#coding:utf-8

"""
ID:          issue-1567
ISSUE:       1567
TITLE:       Server locks up while attempting to commit a deletion of an expression index
DESCRIPTION:
JIRA:        CORE-1145
FBTEST:      bugs.core_1145
NOTES:
    [24.06.2025] pzotov
    ::: NB :::
    SQL schema name (introduced since 6.0.0.834), single and double quotes are suppressed in the output.
    See $QA_HOME/README.substitutions.md or https://github.com/FirebirdSQL/firebird-qa/blob/master/README.substitutions.md

    Checked on 6.0.0.858; 5.0.3.1668; 4.0.6.3214; 3.0.13.33813.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set list on;
    create table expt1 (col1 int);
    create table expt2 (col2 int);
    commit;

    insert into expt1 values (1);
    insert into expt1 values (2);

    insert into expt2 values (1);
    insert into expt2 values (2);
    commit;

    create index iexpt1 on expt1 computed (col1 + 1);
    create index iexpt2 on expt2 computed (col2 + 1);
    commit;

    set plan on;
    select 'point-1' msg, e.* from expt1 e where col1 + 1 = 2;
    select 'point-2' msg, e.* from expt2 e where col2 + 1 = 2;
    commit;

    drop index iexpt2;
    commit; -- lockup

    select 'point-3' msg, e.* from expt1 e where col1 + 1 = 2;
    select 'point-4' msg, e.* from expt2 e where col2 + 1 = 2;
    commit;
"""


# QA_GLOBALS -- dict, is defined in qa/plugin.py, obtain settings
# from act.files_dir/'test_config.ini':
#
addi_subst_settings = QA_GLOBALS['schema_n_quotes_suppress']
addi_subst_tokens = addi_subst_settings['addi_subst']

substitutions = [('[ \t]+', ' ')]
for p in addi_subst_tokens.split(' '):
    substitutions.append( (p, '') )

act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    PLAN (E INDEX (IEXPT1))
    MSG point-1
    COL1 1

    PLAN (E INDEX (IEXPT2))
    MSG point-2
    COL2 1

    PLAN (E INDEX (IEXPT1))
    MSG point-3
    COL1 1

    PLAN (E NATURAL)
    MSG point-4
    COL2 1
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
