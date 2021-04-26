#coding:utf-8
#
# id:           bugs.core_2041
# title:        update or insert with gen_id() with wrong generator value
# decription:   
# tracker_id:   CORE-2041
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE GENERATOR LOGID;

set generator LOGID to 0;

CREATE TABLE LOGBOOK
  ( ID integer not null,
    ENTRY varchar(64),
    PRIMARY KEY (ID));

set term ^ ;

create procedure logrow(txt varchar(64))
as
  declare variable lid integer;
begin
  lid = gen_id(LOGID, 1);
  update or insert into logbook (id, entry)
      values (:lid, :txt);
end^

set term ; ^
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """update or insert into logbook (id, entry) values (gen_id(LOGID, 1), 'Testing 1');
update or insert into logbook (id, entry) values (gen_id(LOGID, 1), 'Testing 2');
update or insert into logbook (id, entry) values (gen_id(LOGID, 1), 'Testing 3');
update or insert into logbook (id, entry) values (gen_id(LOGID, 1), 'Testing 4');
select * from logbook;

execute procedure logrow('Test 1');
execute procedure logrow('Test 2');
execute procedure logrow('Test 3');
execute procedure logrow('Test 4');
select * from logbook;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID ENTRY
============ ================================================================
           1 Testing 1
           2 Testing 2
           3 Testing 3
           4 Testing 4


          ID ENTRY
============ ================================================================
           1 Testing 1
           2 Testing 2
           3 Testing 3
           4 Testing 4
           5 Test 1
           6 Test 2
           7 Test 3
           8 Test 4

"""

@pytest.mark.version('>=2.5.0')
def test_core_2041_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

