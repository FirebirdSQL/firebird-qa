#coding:utf-8

import pytest
from firebird.qa import db_factory, isql_act, Action

init_script = """create table users (
    id integer,
    name varchar(20),
    passwd varchar(20)
);

commit;"""

db = db_factory(init=init_script)

test_script = """create or alter view v_users as
    select name from users;
commit;
show view v_users;
create or alter view v_users (id, name, passwd ) as
    select id, name, passwd  from users;
commit;
show view v_users;
create or alter view v_users_name as
    select name from v_users;
commit;
create or alter view v_users (id, name ) as
    select id, name from users;
commit;
show view v_users;
show view v_users_name;


"""

act = isql_act('db', test_script)

expected_stdout = """ NAME                            VARCHAR(20) Nullable
View Source:
==== ======

    select name from users
ID                              INTEGER Nullable
NAME                            VARCHAR(20) Nullable
PASSWD                          VARCHAR(20) Nullable
View Source:
==== ======

    select id, name, passwd  from users
ID                              INTEGER Nullable
NAME                            VARCHAR(20) Nullable
View Source:
==== ======

    select id, name from users
NAME                            VARCHAR(20) Nullable
View Source:
==== ======

    select name from v_users
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

