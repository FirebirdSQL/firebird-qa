#coding:utf-8
#
# id:           bugs.core_2796
# title:        DB_KEY is always zero for external tables
# decription:   
#                
# tracker_id:   CORE-2796
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table ext_test external file '$(DATABASE_LOCATION)c2796.dat' (col char(24), lf char(1));
    set list on;
    set term ^;
    execute block returns (ms_diff bigint)
    as
        declare dbkey char(8) character set octets;
        declare v_dts1 timestamp;
    begin
        v_dts1=cast('now' as timestamp);
        insert into ext_test values( :v_dts1-rand()*100, ascii_char(10));
        insert into ext_test values( :v_dts1-rand()*100, ascii_char(10));
        insert into ext_test values( :v_dts1-rand()*100, ascii_char(10));
        insert into ext_test values( :v_dts1,            ascii_char(10));
        insert into ext_test values( :v_dts1-rand()*100, ascii_char(10));
    
        select rdb$db_key from ext_test order by col desc rows 1 into :dbkey;
    
        for
            select datediff(millisecond from cast(col as timestamp) to :v_dts1)
            from ext_test
            where rdb$db_key = :dbkey
            into ms_diff
        do
            suspend;
    end 
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MS_DIFF                         0
  """

@pytest.mark.version('>=3.0')
def test_core_2796_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

