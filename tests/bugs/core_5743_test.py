#coding:utf-8
#
# id:           bugs.core_5743
# title:        Conversion error when both GROUP/ORDER BY expressions and WHERE expressions contain literals
# decription:   
#                   Confirmed bug on: 3.0.3.32901, 4.0.0.875.
#                   Minimal requirements for reproduce: 1) boolean field with reference in WHERE clause;  2) indexed integer field.
#                   Checked on:
#                       3.0.4.32912: OK, 1.296s.
#                       4.0.0.800: OK, 2.171s.
#                       4.0.0.890: OK, 1.906s.
#                
# tracker_id:   CORE-5743
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table journal_caisse (
         annule  boolean
        ,periode int
    );    
    create index journal_caisse_idx on journal_caisse (periode);
    set planonly;
    select 1 as type_mvt
    from journal_caisse
    where 
        annule is false
        and 
        (periode = ?)
    group by 1
    ;

    -- sample from CORE-5749:
    select 'my constant ' as dsc, count( * )
    from rdb$relations a
    where a.rdb$system_flag = 99
    group by 1
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN SORT (JOURNAL_CAISSE INDEX (JOURNAL_CAISSE_IDX))
    PLAN SORT (A NATURAL)
"""

@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

