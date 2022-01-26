#coding:utf-8

"""
ID:          issue-6344
ISSUE:       6344
TITLE:       Extend trace record for COMMIT/ROLLBACK RETAINING to allow chaining of transaction ids
DESCRIPTION:
    Test prepares trace config with requrement to watch only for TRANSACTION events.
    Then it starts trace session and makes several changes withing retained Tx.
    (this is done by invocation con.commit() method with argument 'retaining = True').

    Every COMMIT_RETAINING event in the trace log must contain following *new* elements:
    1) "INIT_" token with ID of transaction that originated changes; it must be shown in the same line with "TRA_" info;
    2) "New number <NN>" - ID that will be assigned to the next transaction in this 'chain'; it must be shown in separate line.

    All lines containing "INIT_" must have the same value of transaction that started changes but this value itself can depend
    on FB major version and (maybe) of server mode: CS / SC /SS. For this reason we must save this number as special 'base' that
    will be subtracted from concrete values during parsing of trace lines - see 'tx_base' variable here.

    We parse trace log and pay attention for lines like: "(TRA_nnn, INIT_mmm, ..."  and "New number <XXX>".
    Each interesting numbers are extracted from these lines and <tx_base> is subtracted from them.
    Finally, we display resulting values.
    1) number after phrase "Tx that is origin of changes:" must always be equal to zero;
    2) number after phrase "Tx that finished now" must be:
      2.1) LESS for 1 than value in the next line: "NEW NUMBER" for subsequent Tx..." - for all DML statements EXCEPT LAST;
      2.2) EQUALS to "NEW NUMBER" for subsequent Tx..." for LAST statement because it does not change anything (updates empty table);
JIRA:        CORE-6095
"""

import pytest
import re
from firebird.qa import *

init_script = """
    create sequence g;
    create table test(id int primary key, x int);
    set term ^;
    create trigger test_bi for test active before insert position 0 as
    begin
       new.id = coalesce(new.id, gen_id(g, 1) );
    end
    ^
    create procedure sp_worker(a_x int) as
    begin
        insert into test(x) values(:a_x);
    end
    ^
    set term ;^
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db')

expected_stdout = """
    Found record with "NEW NUMBER" for subsequent Tx numbers:  1
    Found "INIT_" token in "TRA_" record. Tx that is origin of changes:  0 ; Tx that finished now: 1
    Found record with "NEW NUMBER" for subsequent Tx numbers:  2
    Found "INIT_" token in "TRA_" record. Tx that is origin of changes:  0 ; Tx that finished now: 2
    Found record with "NEW NUMBER" for subsequent Tx numbers:  3
    Found "INIT_" token in "TRA_" record. Tx that is origin of changes:  0 ; Tx that finished now: 3
    Found record with "NEW NUMBER" for subsequent Tx numbers:  3
    Found "INIT_" token in "TRA_" record. Tx that is origin of changes:  0 ; Tx that finished now: 3
"""

trace = ['log_initfini = false',
         'log_transactions = true',
         'time_threshold = 0'
         ]

allowed_patterns = [re.compile('\\s*\\(TRA_\\d+,', re.IGNORECASE),
                    re.compile('\\s*New\\s+number\\s+\\d+\\s*', re.IGNORECASE),
                    ]

@pytest.mark.version('>=3.0.6')
def test_1(act: Action, capsys):
    with act.trace(db_events=trace):
        with act.db.connect() as con:
            cur = con.cursor()
            con.execute_immediate('insert into test(x) values(123)')
            con.commit(retaining = True)                    # (TRA_12, ... ; next line: "New number 13"
            cur.callproc('sp_worker', [456])                # (TRA_13, INIT_12, ...
            con.commit(retaining = True)                    # (TRA_13, INIT_12, ... ; next line: "New number 14"
            con.execute_immediate('delete from test')       # (TRA_14, INIT_12, ...
            con.commit(retaining = True)                    # (TRA_14, INIT_12, ... ; next line: "New number 15"
            # This statement does not change anything:
            con.execute_immediate('update test set x = -x') # (TRA_15, INIT_12, ...
            con.commit(retaining = True)                    # (TRA_15, INIT_12, ... ; next line: "New number 15" -- THE SAME AS PREVIOUS!
    # Process trace
    tx_base = -1
    for line in act.trace_log:
        if line.rstrip().split():
            for p in allowed_patterns:
                if p.search(line):
                    if '(TRA_' in line:
                        words = line.replace(',',' ').replace('_',' ').replace('(',' ').split()
                        # Result:
                        # 1) for tx WITHOUT retaining: ['TRA', '12', 'READ', 'COMMITTED', '|', 'REC', 'VERSION', '|', 'WAIT', '|', 'READ', 'WRITE)']
                        # 2) for tx which is RETAINED: ['TRA', '13', 'INIT', '12', 'READ', 'COMMITTED', '|', 'REC', 'VERSION', '|', 'WAIT', '|', 'READ', 'WRITE)']
                        #                                 0      1     2       3
                        tx_base = int(words[1]) if tx_base == -1 else tx_base
                        if words[2] == 'INIT':
                            tx_origin_of_changes = int(words[3]) - tx_base
                            tx_that_finished_now = int(words[1]) - tx_base
                            print('Found "INIT_" token in "TRA_" record. Tx that is origin of changes: ', tx_origin_of_changes, '; Tx that finished now:', tx_that_finished_now)
                    elif 'number' in line:
                        tx_for_subsequent_changes = int(line.split()[2]) - tx_base # New number 15 --> 15
                        print('Found record with "NEW NUMBER" for subsequent Tx numbers: ', tx_for_subsequent_changes)
    #
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
