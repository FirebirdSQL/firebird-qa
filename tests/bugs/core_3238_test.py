#coding:utf-8
#
# id:           bugs.core_3238
# title:        Makes GEN_UUID return a compliant RFC-4122 UUID
# decription:   
# tracker_id:   CORE-3238
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set term ^;
    execute block returns(err_cnt int) as
      declare n int = 100000;
      declare s varchar(36);
    begin
      err_cnt = 0;
      while( n > 0 ) do
      begin
        s = uuid_to_char( gen_uuid() );
        if ( NOT (substring(s from 15 for 1)='4' and substring(s from 20 for 1) in ('8','9','A','B')) )
          then err_cnt = err_cnt + 1;
        n = n - 1;
      end
      suspend;
    end
    ^ set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ERR_CNT                         0
"""

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

