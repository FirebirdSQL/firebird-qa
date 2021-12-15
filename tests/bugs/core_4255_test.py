#coding:utf-8
#
# id:           bugs.core_4255
# title:        Parametrized queries using RDB$DB_KEY do not work
# decription:
# tracker_id:   CORE-4255
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- test by Mark:
    recreate table dbkeytest
    (
        id integer primary key,
        seen boolean default false
    );
    commit;
    insert into dbkeytest (id) values (1);
    insert into dbkeytest (id) values (2);
    insert into dbkeytest (id) values (3);
    insert into dbkeytest (id) values (4);
    commit;

    -- actual test:
    set term ^;
    execute block
    as
        declare thekey char(8);
        declare theid integer;
    begin
        for select id, rdb$db_key from dbkeytest into theid, thekey do
        begin
            execute statement ('update dbkeytest set seen = true where rdb$db_key = ?') (thekey);
        end
    end
    ^
    set term ;^
    commit;

    select * from dbkeytest;

    -- one else test (suggested by Dmitry) in this ticket:
    select 1 x from rdb$database where rdb$db_key = cast((select rdb$db_key from rdb$database) as varchar(8));
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
              ID    SEEN
    ============ =======
               1 <true>
               2 <true>
               3 <true>
               4 <true>

               X
    ============
               1
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.db.set_async_write()
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

