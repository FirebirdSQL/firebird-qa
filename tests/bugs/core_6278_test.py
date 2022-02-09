#coding:utf-8

"""
ID:          issue-6520
ISSUE:       6520
TITLE:       Efficient table scans for DBKEY-based range conditions
DESCRIPTION:
  We create table with very wide column and add there about 300 rows from rdb$types, with random data
  (in order to prevent RLE-compression which eventually can reduce number of data pages).
  Then we extract all values of rdb$db_key from this table and take into processing two of them.
  First value has 'distance' from starting db_key = 1/3 of total numbers of rows, second has similar
  distance from final db_key.
  Finally we launch trace and start query with SCOPED expression for RDB$DB_KEY:
    select count(*) from tmp_test_6278 where rdb$db_key between ? and ?

  Trace must contain after this explained plan with "lower bound, upper bound" phrase and table statistics
  which shows number of reads = count of rows plus 1.

  Before fix trace table statistics did not reflect scoped WHERE-expression on RDB$DB_KEY column.
JIRA:        CORE-6278
FBTEST:      bugs.core_6278
"""

import pytest
import re
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
    -> Table "TMP_TEST_6278" Full Scan (lower bound, upper bound)
    Reads difference: EXPECTED.
"""

test_script = """
    recreate table tmp_test_6278 (s varchar(32700)) ;
    insert into tmp_test_6278 select lpad('', 32700, uuid_to_char(gen_uuid())) from rdb$types ;
    commit ;
    set heading off ;
    set term ^ ;
    execute block returns(
       count_intermediate_rows int
    ) as
        declare dbkey_1 char(8) character set octets ;
        declare dbkey_2 char(8) character set octets ;
        declare sttm varchar(255) ;
    begin
       select max(iif( ri=1, dbkey, null)), max(iif( ri=2, dbkey, null))
       from (
           select dbkey, row_number()over(order by dbkey) ri
           from (
               select
                   dbkey
                  ,row_number()over(order by dbkey) ra
                  ,row_number()over(order by dbkey desc) rd
               from (select rdb$db_key as dbkey from tmp_test_6278)
           )
           where
               ra = (ra+rd)/3
               or rd = (ra+rd)/3
       ) x
       into dbkey_1, dbkey_2 ;

       sttm = q'{select count(*) from tmp_test_6278 where rdb$db_key between ? and ?}' ;
       execute statement (sttm) (dbkey_1, dbkey_2) into count_intermediate_rows ;
       suspend ;
    end ^
    set term ; ^
    commit ;
"""

trace = ['log_statement_finish = true',
         'print_plan = true',
         'print_perf = true',
         'explain_plan = true',
         'time_threshold = 0',
         'log_initfini = false',
         'exclude_filter = "%(execute block)%"',
         'include_filter = "%(select count)%"',
         ]


@pytest.mark.version('>=4.0')
def test_1(act: Action, capsys):
    allowed_patterns = [re.compile(' Table "TMP_TEST_6278"', re.IGNORECASE),
                        re.compile('TMP_TEST_6278\\s+\\d+', re.IGNORECASE)
                        ]
    # For yet unknown reason, trace must be read as in 'cp1252' (neither ascii or utf8 works)
    with act.trace(db_events=trace, encoding='cp1252'):
        act.isql(switches=['-q'], input=test_script)
    # Process isql output
    for line in act.clean_stdout.splitlines():
        if elements := line.rstrip().split():
            count_intermediate_rows = int(elements[0])
            break
    # Process trace
    for line in act.trace_log:
        for p in allowed_patterns:
            if p.search(line):
                if line.startswith('TMP_TEST_6278'):
                    trace_reads_statistics = int(line.rstrip().split()[1])
                    result = ('EXPECTED.' if (trace_reads_statistics - count_intermediate_rows) <= 1
                              else f'UNEXPECTED: {trace_reads_statistics - count_intermediate_rows}')
                    print(f'Reads difference: {result}')
                else:
                    print(line)
    # Check
    act.reset() # necessary to reset 'clean_stdout' !!
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
