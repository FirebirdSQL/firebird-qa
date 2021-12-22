#coding:utf-8
#
# id:           bugs.core_2890
# title:        SQLSTATE should also be available as a PSQL context variable like GDSCODE/SQLCODE
# decription:   
#                  ::: NOTE :::
#                  Despite of ticket's issue that it was fixed to 2.5.1, test script from here will output
#                  NOT ALL rows in WI-V2.5.1.26351 (official 2.5.1 release):
#               
#                   RES_SQLCODE                     -901
#                   RES_GDSCODE                     335544345
#                   RES_SQLSTATE                    40001
#               
#                   RES_SQLCODE                     -802
#                   RES_GDSCODE                     335544321
#                   RES_SQLSTATE                    22012
#               
#                   These data:
#                     RES_SQLCODE                     -803
#                     RES_GDSCODE                     335544665
#                     RES_SQLSTATE                    23000
#                   -- will not be displayed.
#                  For this reason it was decided to specify min_version = 2.5.2 rather than 2.5.1
#                
# tracker_id:   CORE-2890
# min_versions: ['2.5.2']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core2890.fbk', init=init_script_1)

test_script_1 = """
    commit;
    set transaction no wait;
    
    update test set id = -id where id = 2;

    set list on;

    set term ^;
    execute block returns(res_sqlcode int, res_gdscode int, res_sqlstate char(5)) as
    begin
        for
            select res_sqlcode, res_gdscode, res_sqlstate
            from sp_test('I')
            into res_sqlcode, res_gdscode, res_sqlstate
        do
           suspend;
        -------------------------------------
        for
            select res_sqlcode, res_gdscode, res_sqlstate
            from sp_test('D')
            into res_sqlcode, res_gdscode, res_sqlstate
        do
           suspend;
        -------------------------------------
        for
            select res_sqlcode, res_gdscode, res_sqlstate
            from sp_test('U')
            into res_sqlcode, res_gdscode, res_sqlstate
        do
           suspend;
    end
    ^
    set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RES_SQLCODE                     -803
    RES_GDSCODE                     335544665
    RES_SQLSTATE                    23000

    RES_SQLCODE                     -913
    RES_GDSCODE                     335544336
    RES_SQLSTATE                    40001

    RES_SQLCODE                     -802
    RES_GDSCODE                     335544321
    RES_SQLSTATE                    22012
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

