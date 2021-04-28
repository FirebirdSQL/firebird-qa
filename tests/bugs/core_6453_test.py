#coding:utf-8
#
# id:           bugs.core_6453
# title:        EXECUTE STATEMENT fails on FB 4.x if containing time/timestamp with time zone parameters
# decription:   
#                   Confirmed bug on 4.0.0.2265
#                   Checked on 4.0.0.2303; 3.0.8.33393; 2.5.9.27152
#                
# tracker_id:   CORE-6453
# min_versions: ['2.5']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block as
        declare sttm varchar(100);
        declare result varchar(100);
    begin
        sttm = 'select current_time from rdb$database';
        execute statement sttm into result;

        sttm = 'select current_timestamp from rdb$database';
        execute statement sttm into result;
    end
    ^
    set term ;^ 

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.execute()

