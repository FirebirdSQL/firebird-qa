#coding:utf-8

"""
ID:          issue-3043
ISSUE:       3043
TITLE:       Unique index with a lot of NULL keys can be corrupted at level 1
DESCRIPTION:
JIRA:        CORE-2635
FBTEST:      bugs.core_2635
"""

import pytest
from firebird.qa import *

init_script = """set term ^;
recreate table t (id int, sss varchar(255)) ^
create unique descending index t_id_desc on t (id) ^
create unique ascending  index t_id_asc  on t (id) ^
create unique descending index t_id_sss_desc on t (id, sss) ^
create unique ascending  index t_id_sss_asc  on t (id, sss) ^
commit ^

execute block as
declare n int = 0;
begin
  while (n < 10000) do
  begin
    insert into t values (:n, :n);
    n = n + 1;
  end

  n = 0;
  while (n < 10000) do
  begin
    insert into t values (null, null);
    n = n + 1;
  end
end ^
commit ^

execute block as
declare n int = 5000;
begin
  while (n > 0) do
  begin
    n = n - 1;
    update t set id = null, sss = null where id = :n;
  end
end ^
commit ^
"""

db = db_factory(init=init_script)

act = python_act('db', substitutions=[('[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9]', ''),
                                        ('Relation [0-9]{3,4}', 'Relation')])

expected_stdout = """
Validation started
Relation (T)
process pointer page    0 of    1
Index 1 (T_ID_DESC)
Index 2 (T_ID_ASC)
Index 3 (T_ID_SSS_DESC)
Index 4 (T_ID_SSS_ASC)
Relation (T) is ok
Validation finished
"""

@pytest.mark.version('>=2.5')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    with act.connect_server() as srv:
        srv.database.validate(database=act.db.db_path)
        act.stdout = '\n'.join(srv.readlines())
    assert act.clean_stdout == act.clean_expected_stdout
