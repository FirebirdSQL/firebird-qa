#coding:utf-8
#
# id:           bugs.core_3306
# title:        Invariant sub-query is treated as variant thus causing multiple invokations of a nested stored procedure
# decription:   
# tracker_id:   CORE-3306
# min_versions: ['2.5.1']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """SET TERM !!;
Create Table tt_table(Field1 varchar(100))!!
Create Or Alter PROCEDURE SPR_TEST (pName Varchar(2000)) RETURNS (sValue Varchar(255)) AS
BEGIN
  Insert Into tt_table(field1) values(:pName);
  sValue=:pName;
  suspend;
End!!
COMMIT!!
SET TERM ;!!
Select count(*)
from rdb$types
where rdb$field_name like (select sValue From spr_test('SIMSIM'));
COMMIT;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """Select count(*) From tt_table;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                COUNT
=====================
                    1

"""

@pytest.mark.version('>=3.0')
def test_core_3306_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

