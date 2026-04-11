#coding:utf-8

"""
ID:       n/a
ISSUE:    https://groups.google.com/g/firebird-devel/c/DfxVxtU3Iuk
TITLE:    GTT behavior changed in master (issue in fb-devel).
DESCRIPTION: 
    GTT with attribute 'ON COMMIT PRESERVE ROWS' became empty when another table is dropped within same transaction.
NOTES:
    [11.04.2026] pzotov
    DML against GTT and 'DROP TABLE <some_other_name>' must be executed in the same transaction.
    Confirmed bug on 6.0.0.1887-2e18929.
    Checked on 6.0.0.1887-2e18929
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set autoddl off; -- [ ! ]
    set list on;

    create global temporary table gtt_pub(
        id int
    ) on commit preserve rows;

    create table t_drop(
        id int
    );
    commit;

    insert into gtt_pub(id) values (1);
    select id as gtt_pub_id_before from gtt_pub;

    drop table t_drop;
    commit;

    set count on;
    select id as gtt_pub_id_after from gtt_pub;
"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    GTT_PUB_ID_BEFORE 1
    GTT_PUB_ID_AFTER  1
    Records affected: 1
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
