#coding:utf-8
#
# id:           bugs.core_6290
# title:        Hex number used at end of statement (e.g. CREATE DOMAIN ... DEFAULT) may read invalid memory and produce wrong values or exceptions
# decription:   
#                   Checked on 3.0.6.33289, 4.0.0.1931.
#                
# tracker_id:   CORE-6290
# min_versions: []
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- All following statements should not produce neither STDOUT nor STDERR:

    create domain dm_test_01 as double precision default 100000000;
    create domain dm_test_02 as bigint default 0xf0000000;
    ----------------------------------------------------------------
    create domain dm_test_03 as int default 1;
    create domain dm_test_04 as bigint default 0xf0000000; 
    ----------------------------------------------------------------
    create domain dm_test_05 as date default 'TODAY';
    create domain dm_test_06 as bigint default 0x0F0000000; 
    ----------------------------------------------------------------
    create domain dm_test_07 as boolean default true;
    create domain dm_test_08 as bigint default 0x0F0000000;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.6')
def test_1(act_1: Action):
    act_1.execute()

