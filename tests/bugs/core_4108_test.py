#coding:utf-8
#
# id:           bugs.core_4108
# title:        Regression: Server crashes when executing sql query "delete from mytable order by id desc rows 2"
# decription:   
# tracker_id:   CORE-4108
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
    create table mytable (
        id integer not null primary key,
        name varchar(30)
    );

    insert into mytable(id, name)
    select 1, 'a' from rdb$database
    union all
    select 2, 'b' from rdb$database
    union all
    select 3, 'c' from rdb$database;
    
    delete from mytable order by id desc rows 2;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.execute()

