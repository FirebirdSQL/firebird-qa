#coding:utf-8

"""
ID:          issue-5197
ISSUE:       5197
TITLE:       Invalid internal BLR filter conversion
DESCRIPTION:
JIRA:        CORE-4905
FBTEST:      bugs.core_4905
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create or alter procedure sp_test(field_name type of column rdb$types.rdb$field_name) as
    begin
    end
    ^
    set term ;^
    commit;
    set list on;
    set blob all;
    select cast(p.rdb$procedure_blr as blob sub_type text) sp_blr_blob
    from rdb$procedures p
    where p.rdb$procedure_name = upper('SP_TEST');
"""

act = isql_act('db', test_script, substitutions=[('SP_BLR_BLOB.*', '')])

expected_stdout = """
    blr_version5,blr_begin,    blr_message, 0, 2,0,       blr_column_name, 0, 9, 'R','D','B','$','T','Y','P','E','S', 14, 'R','D','B','$','F','I','E','L','D','_','N','A','M','E',      blr_short, 0,    blr_message, 1, 1,0,       blr_short, 0,    blr_receive, 0,       blr_begin,          blr_stall,          blr_label, 0,             blr_begin,                blr_end,          blr_end,    blr_send, 1,       blr_begin,          blr_assignment,             blr_literal, blr_short, 0, 0,0,            blr_parameter, 1, 0,0,          blr_end,    blr_end, blr_eoc
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

