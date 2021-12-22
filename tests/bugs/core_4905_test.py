#coding:utf-8
#
# id:           bugs.core_4905
# title:        Invalid internal BLR filter conversion
# decription:   
# tracker_id:   CORE-4905
# min_versions: ['2.5.5']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('SP_BLR_BLOB.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    blr_version5,blr_begin,    blr_message, 0, 2,0,       blr_column_name, 0, 9, 'R','D','B','$','T','Y','P','E','S', 14, 'R','D','B','$','F','I','E','L','D','_','N','A','M','E',      blr_short, 0,    blr_message, 1, 1,0,       blr_short, 0,    blr_receive, 0,       blr_begin,          blr_stall,          blr_label, 0,             blr_begin,                blr_end,          blr_end,    blr_send, 1,       blr_begin,          blr_assignment,             blr_literal, blr_short, 0, 0,0,            blr_parameter, 1, 0,0,          blr_end,    blr_end, blr_eoc
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

