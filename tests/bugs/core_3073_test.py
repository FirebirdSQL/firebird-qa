#coding:utf-8
#
# id:           bugs.core_3073
# title:        Foreign key cascade with SET DEFAULT uses the default value of the moment of the FK creation
# decription:   
#                   Confirmed bug on WI-T4.0.0.503.
#                   Checked on WI-T4.0.0.511 - works fine.
#                
# tracker_id:   CORE-3073
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table tdetl(x int);
    recreate table tmain(x int);
    commit;
    set term ^;
    execute block as
    begin
      execute statement 'drop domain dm_name';
      when any do begin end
    end
    ^
    set term ;^
    commit;

    create domain dm_name varchar(15) default 'Old Trafford';
    commit;

    recreate table tmain(name dm_name primary key);
    recreate table tdetl(name dm_name references tmain on delete set default);
    commit;

    alter domain dm_name set default 'New Vasyuki';
    commit;

    insert into tmain values('London');
    insert into tmain values('Old Trafford');
    insert into tmain values('New Vasyuki');

    insert into tdetl values('London');
    insert into tdetl values('Old Trafford');

    set list on;

    select 'before cascade on tdetl' as msg, d.* from tdetl d;
    delete from tmain where name = 'London';
    select 'after cascade on tdetl' as msg, d.* from tdetl d;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             before cascade on tdetl
    NAME                            London
    MSG                             before cascade on tdetl
    NAME                            Old Trafford

    MSG                             after cascade on tdetl
    NAME                            New Vasyuki
    MSG                             after cascade on tdetl
    NAME                            Old Trafford
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

