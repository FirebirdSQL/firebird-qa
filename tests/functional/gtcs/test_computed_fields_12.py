#coding:utf-8

"""
ID:          computed-fields-12
FBTEST:      functional.gtcs.computed_fields_12
TITLE:       Computed fields
DESCRIPTION:
  Original test see in:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_12.script
  SQL script for creating test database ('gtcs_sp1.fbk') and fill it with some data:
  https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/PROCS_QA_INIT_ISQL.script
NOTES:
[25.09.2021]
  moved code for 4.0+ into separate secion because of fixed gh-6845. Use SET_SQLDA_DISPLAY ON for check datatypes.
  (seel also commit for apropriate GTCS-tests: e617f3d70be5018de6e6ee8624da6358d52a9ce0, 20-aug-2021 14:11)
"""

import pytest
from firebird.qa import *

db = db_factory()

# version: 3.0

test_script_1 = """
    set heading off;
    set list on;
    /*---------------------------------------------*/
    /* Computed field using another computed field */
    /*---------------------------------------------*/
    create table t3 (a integer, af computed by (a*3), afaf computed by (af*2));
    insert into t3(a) values(10);

    select * from t3;
"""

act_1 = isql_act('db', test_script_1, substitutions=[('[ \t]+', ' ')])

expected_stdout_1 = """
    A                               10
    AF                              30
    AFAF                            60
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0

test_script_2 = """
    set list on;
    recreate table test (fld_source integer, fld_comp_based_on_source computed by ( fld_source*3 ), fld_comp_based_on_comp computed by ( fld_comp_based_on_source * 2 ) );
    insert into test(fld_source) values(10);

    set sqlda_display on;

    -- expected output for 3rd column:
    -- 03: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16" (confirm on build 4.0.1.2613; 5.0.0.220)
    -- build 4.0.1.2536 (last before fix) issues here "03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8"

    select * from test;
"""

act_2 = isql_act('db', test_script_2, substitutions=[('^((?!(sqltype|FLD_)).)*$', ''),
                                                     ('[ \t]+', ' '), ('.*alias.*', '')])

expected_stdout_2 = """
    01: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
    02: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    03: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
    FLD_SOURCE                      10
    FLD_COMP_BASED_ON_SOURCE        30
    FLD_COMP_BASED_ON_COMP                                                     60
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout
