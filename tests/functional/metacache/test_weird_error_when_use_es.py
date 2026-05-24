#coding:utf-8

"""
ID:          n/a
ISSUE:       n/a
TITLE:       Weird message (with irrelevant text) raises when AUTODDL = OFF and attempt to call procedure which was created using ES and uses ES for some DML.
DESCRIPTION:
    Bug was found occasionally during attempt to re-implement test for CORE-6336: code below "INSERT operation is not allowed for system table RDB$PAGES"
    on major FB versions 3.x ... 5.x, but on 6.x it runs OK. Probably, this outcome in 6.x relates to shared metacache (at least up to 6.0.0.1465-3bbe725).
    See letter to FB team 13.05.2026 0228. Reply from Alex 24.05.2026 1904.
NOTES:
    [24.05.2026] pzotov
    Checked on 6.0.0.1965-f9a8d1a.
"""

import pytest
from firebird.qa import *

test_sql = f"""
    set heading off;
    set autoddl off; -- [ 1 ]
    commit;

    --recreate table t_info(f_name varchar(10));
    set term ^;
    create procedure sp_add_objects as
    begin
        execute statement 'recreate table t_info(f_name varchar(10))';
        execute statement
            q'#create procedure sp_test(a_input_mode varchar(10) = '') as
               begin
                   if ( a_input_mode = 'es' ) then
                       execute statement ('insert into t_info(f_name) values(?)') ('bar'); -- [ 2 ]
                   else
                       insert into t_info(f_name) values('foo'); -- [ 3 ]
               end
            #';
    end
    ^
    set term ;^
    commit;

    execute procedure sp_add_objects;
    --commit;

    set bail off;
    execute procedure sp_test('es');

    execute procedure sp_test;

    set count on;
    select * from t_info;
"""

db = db_factory()
act = isql_act('db', test_sql)

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stdout = f"""
        bar
        foo
        Records affected: 2
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
