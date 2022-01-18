#coding:utf-8

"""
ID:          issue-1175
ISSUE:       1175
TITLE:       Alter view
DESCRIPTION:
JIRA:        CORE-790
"""

import pytest
from firebird.qa import *

init_script = """create table users (
    id integer,
    name varchar(20),
    passwd varchar(20)
);

create view v_users as
    select name from users;
commit;"""

db = db_factory(init=init_script)

test_script = """alter view v_users (id, name, passwd ) as
    select id, name, passwd  from users;
commit;
show view v_users;
create view v_users_name as
    select name from v_users;
commit;
alter view v_users (id, name ) as
    select id, name from users;
commit;
show view v_users;
show view v_users_name;


"""

act = isql_act('db', test_script)

expected_stdout = """Database:  test.fdb, User: SYSDBA
SQL> CON> SQL> SQL> ID                              INTEGER Nullable
NAME                            VARCHAR(20) Nullable
PASSWD                          VARCHAR(20) Nullable
View Source:
==== ======

    select id, name, passwd  from users
SQL> CON> SQL> SQL> CON> SQL> SQL> ID                              INTEGER Nullable
NAME                            VARCHAR(20) Nullable
View Source:
==== ======

    select id, name from users
SQL> NAME                            VARCHAR(20) Nullable
View Source:
==== ======

    select name from v_users
SQL> SQL> SQL> SQL>
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

