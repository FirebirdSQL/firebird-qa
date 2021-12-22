#coding:utf-8
#
# id:           bugs.core_1797
# title:        OLD/NEW.RDB$DB_KEY returns incorrect result in triggers
# decription:   
# tracker_id:   CORE-1797
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t (n integer) ;
create table x (c char(8) character set octets);
set term ^ ;
create trigger t_ai for t after insert
as
begin
  insert into x values (new.rdb$db_key);
end ^
set term ; ^
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """insert into t values (1) returning rdb$db_key;

select rdb$db_key from t;
select * from x;

insert into t values (2) returning rdb$db_key;

select rdb$db_key from t;
select * from x;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
DB_KEY
================
8000000001000000


DB_KEY
================
8000000001000000


C
================
8000000001000000


DB_KEY
================
8000000002000000


DB_KEY
================
8000000001000000
8000000002000000


C
================
8000000001000000
8000000002000000

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

