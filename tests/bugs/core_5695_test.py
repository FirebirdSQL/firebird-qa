#coding:utf-8
#
# id:           bugs.core_5695
# title:        Position function does not consider the collation for blob
# decription:
#                   Confirmed bug on 3.0.3.32837, 4.0.0.800
#                   Checked on:
#                       FB30SS, build 3.0.3.32876: OK, 1.094s.
#                       FB40SS, build 4.0.0.852: OK, 1.109s.
#
# tracker_id:   CORE-5695
# min_versions: ['3.0.3']
# versions:     3.0.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set blob all;
    set term ^;
    execute block returns (res smallint) as
        declare blb blob sub_type 1 segment size 80 collate unicode_ci;
        declare txt varchar(255) collate unicode_ci;
    begin
        -- pure ASCII strings:
        blb = 'A';
        txt = 'a';
        res = position(txt, blb);
        suspend;
        -- strings with NON-ascii characters:
        blb=  'ŁÁTÉÇØΙΚΌΛΑΟΣ';
        txt = 'Łátéçøικόλαος';
        res = position(txt, blb);
        suspend;
    end
    ^
    set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RES                             1
    RES                             1
"""

@pytest.mark.version('>=3.0.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute(charset='utf8')
    assert act_1.clean_expected_stdout == act_1.clean_stdout

