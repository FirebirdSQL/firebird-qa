#coding:utf-8
#
# id:           bugs.core_4623
# title:        Regression: SP "Domain" and "Type Of" based variables referring BLOB with sub_type < 0 no longer work
# decription:   
# tracker_id:   CORE-4623
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter procedure sp_test as begin end;
    recreate table test (id int);
    commit;
    set term ^;
    execute block as
    begin
        execute statement 'drop domain dm_01';
    when any do begin end
    end
    ^
    set term ;^
    commit;
    
    create domain dm_01 as blob sub_type -32768 segment size 32000;
    recreate table test (b_field dm_01);
    commit;
    
    set term ^;
    create or alter procedure sp_test (
        b01 blob sub_type -32768 segment size 32000,
        b02 type of column test.b_field,
        b03 dm_01
    ) as
    begin
    end
    ^
    create or alter trigger test_bi0 for test active before insert position 0 as
        declare b01 blob sub_type -32768 segment size 32000;
        declare b02 type of column test.b_field;
        declare b03 dm_01;
    begin
    end
    ^
    set term ;^
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.execute()

