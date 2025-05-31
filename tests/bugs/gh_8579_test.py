#coding:utf-8

"""
ID:          issue-8579
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8579
TITLE:       Add sub routines info in the BLR debug blob filter
DESCRIPTION:
    Test creates procedure (sp_main) and function (fn_main) and each contains <SUBROUTINES_COUNT> declarations
    of inner procedures and <SUBROUTINES_COUNT> functions.
    Then we run query 'select rdb$debug_info from rdb$...' and check that line line 'BLR to Source mapping:'
    occurs exactly <SUBROUTINES_COUNT> times for each kind sub-routine.
NOTES:
    [31.05.2025] pzotov
    If we try to declare inner procedures 19 times then line 'BLR to Source mapping:' appears to be "broken"
    for last (19th) sub-routine. Because of this, test currently must use no more than 18 declarations.
    Sent report to Adriano, waiting for fix.

    Checked on 6.0.0.792-d90992f.
"""
import pytest
from firebird.qa import *

SUBROUTINES_COUNT = 18 # 31.05.2025: 19 - broken line 'BLR to Source mapping:' !
BLR_TO_SOURCE_TXT = 'BLR to Source mapping:'
substitutions = [ ('^((?!' + BLR_TO_SOURCE_TXT + '|Sub function|Sub procedure).)*$', '') ]

db = db_factory()
act = python_act('db', substitutions = substitutions)

expected_lst = []

proc_ddl = [  'create procedure sp_main as' ]
for i in range(SUBROUTINES_COUNT):
    proc_ddl.extend( [f'  declare function sp_main_sub_func_{i:05} returns int as', '  begin', f'    return {i};', '  end'] )
    expected_lst.extend([BLR_TO_SOURCE_TXT, f'Sub function SP_MAIN_SUB_FUNC_{i:05}:'])

for i in range(SUBROUTINES_COUNT):
    proc_ddl.extend( [f'  declare procedure sp_main_sub_proc_{i:05} as', '    declare n int;', '  begin', f'    n = {i};', '  end'] )
    expected_lst.extend([BLR_TO_SOURCE_TXT, f'Sub procedure SP_MAIN_SUB_PROC_{i:05}:'])
proc_ddl.extend( ['begin', 'end'] )

expected_lst.append(BLR_TO_SOURCE_TXT)

#..........................................................................................

func_ddl = [  'create function fn_main returns int as' ]
for i in range(SUBROUTINES_COUNT):
    func_ddl.extend( [f'  declare function fn_main_sub_func_{i:05} returns int as', '  begin', f'    return {i};', '  end'] )
    expected_lst.extend([BLR_TO_SOURCE_TXT, f'Sub function FN_MAIN_SUB_FUNC_{i:05}:'])

for i in range(SUBROUTINES_COUNT):
    func_ddl.extend( [f'  declare procedure fn_main_sub_proc_{i:05} as', '    declare n int;', '  begin', f'    n = {i};', '  end'] )
    expected_lst.extend([BLR_TO_SOURCE_TXT, f'Sub procedure FN_MAIN_SUB_PROC_{i:05}:'])
func_ddl.extend( ['begin', '  return 1;', 'end'] )

expected_lst.append(BLR_TO_SOURCE_TXT)

#-----------------------------------------------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    with act.db.connect(charset = 'utf8') as con:
        con.execute_immediate('\n'.join([x.strip() for x in proc_ddl]))
        con.execute_immediate('\n'.join([x.strip() for x in func_ddl]))
        con.commit()
    
    sources_map = { 'rdb$procedures' : ('rdb$procedure_name', 'sp_main'), 'rdb$functions' : ('rdb$function_name', 'fn_main') }
    for k,v in sources_map.items():
        check_sql = f"set heading off; set blob all; select p.rdb$debug_info as blob_debug_info from {k} p where p.{v[0]} = upper('{v[1]}');"
        act.isql(switches = ['-q'], input = check_sql, combine_output = True)
        print(act.stdout)
        act.reset()

    act.expected_stdout = '\n'.join(expected_lst)
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
