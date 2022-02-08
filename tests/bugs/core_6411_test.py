#coding:utf-8

"""
ID:          issue-6649
ISSUE:       6649
TITLE:       FB crashes on attempt to create table with number of fields greater than 5460
DESCRIPTION:
  It was found that maximal number of fields with type = BIGINT that could fit in a table DDL is 8066.
  If this limit is exeeded then FB raises "new record size of N bytes is too big" (where N >= 65536).
  We use for-loop with two iterations, each of them does following:
    1. Create table with total number of fields = <N> (one for 'ID primary key' plus 8064 for
       'user-data' fields with names 'F1', 'F2', ..., 'F'<N>-1). All of them have type = BIGINT.
    2. DO RECONNECT // mandatory! otherwise crash can not be reproduced.
    3. Run UPDATE OR INSERT statement that is specified in the ticker(insert single record with ID=1).
    4. Run SELECT statement which calculates total sum on all 'user-data' fields.
  When N = 8065 then these actions must complete successfully and result of final SELECT must be displayed.
  When N = 8066 then we have to get exception:
    Statement failed, SQLSTATE = 54000
    unsuccessful metadata update
    -new record size of 65536 bytes is too big

  Confirmed bug on 4.0.0.2204: got crash when N=8065 (but still "new record size of 65536 bytes is too big" when N=8066).
  Checked on 3.0.7.33368, 4.0.0.2214 - all OK.
NOTES:
[08.02.2022] pcisar
  Fails on Windows 3.0.8 with diff:
           step: 0, FLD_COUNT: 8064, result: FIELDS_TOTAL 32510016
           step: 1, FLD_COUNT: 8065, result: Statement failed, SQLSTATE = 54000
           step: 1, FLD_COUNT: 8065, result: unsuccessful metadata update
           step: 1, FLD_COUNT: 8065, result: -new record size of 65536 bytes is too big
         - step: 1, FLD_COUNT: 8065, result: -TABLE TDATA
         + step: 1, FLD_COUNT: 8065, result: -TABLE TDATA
         ?                                               +
         + step: 1, FLD_COUNT: 8065, result: Statement failed, SQLSTATE = 21S01
         + step: 1, FLD_COUNT: 8065, result: Dynamic SQL Error
         + step: 1, FLD_COUNT: 8065, result: -SQL error code = -804
         + step: 1, FLD_COUNT: 8065, result: -Count of read-write columns does not equal count of values
JIRA:        CORE-6411
FBTEST:      bugs.core_6411
"""

import pytest
import platform
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[('.*(-)?After line \\d+.*', ''), ('[ \t]+', ' ')])

expected_stdout = """
    step: 0, FLD_COUNT: 8064, result: FIELDS_TOTAL 32510016
    step: 1, FLD_COUNT: 8065, result: Statement failed, SQLSTATE = 54000
    step: 1, FLD_COUNT: 8065, result: unsuccessful metadata update
    step: 1, FLD_COUNT: 8065, result: -new record size of 65536 bytes is too big
    step: 1, FLD_COUNT: 8065, result: -TABLE TDATA
"""

@pytest.mark.skipif(platform.system() == 'Windows', reason='FIXME: see notes')
@pytest.mark.version('>=3.0.7')
def test_1(act: Action, capsys):
    for step in range(2):
        FLD_COUNT = 8064 + step
        ddl_init = 'recreate table tdata (id bigint primary key'
        ddl_addi = '\n'.join([f',f{i} bigint' for i in range(1,FLD_COUNT)])
        ddl_expr = ''.join([ddl_init, ddl_addi, ')'])
        upd_init = 'update or insert into tdata values(1'
        upd_addi = '\n'.join( [f',{i}' for i in range(1,FLD_COUNT)])
        upd_expr = ''.join([upd_init, upd_addi, ') matching(id)'])
        sel_init = 'select '
        sel_addi = '+'.join([str(i) for i in range(0,FLD_COUNT)])
        sel_expr = ''.join([sel_init, sel_addi, ' as fields_total from tdata'])
        sql_expr=  f"""
            set bail on ;
            {ddl_expr} ;
            commit;
            connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}' ;
            {upd_expr} ;
            set list on ;
            {sel_expr} ;
            quit ;
            """
        act.reset()
        act.isql(switches=[], input=sql_expr, combine_output=True)
        for line in act.clean_stdout.splitlines():
            if line.strip():
                print(f'step: {step}, FLD_COUNT: {FLD_COUNT}, result: {line}')
    # Check
    act.reset()
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
