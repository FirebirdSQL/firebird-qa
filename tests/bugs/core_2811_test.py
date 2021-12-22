#coding:utf-8
#
# id:           bugs.core_2811
# title:        Unsuccessful execution' error when updating a record
# decription:   CREATE OR ALTER TRIGGER NEW_TRIGGER FOR NEW_TABLE
#               ACTIVE AFTER UPDATE POSITION 20
#               AS
#               -- Typically this variable would be used in the trigger. To make it simple, I've
#               -- removed all code possible to still get the error.
#               declare variable NewHours numeric(9,2) = 0;
#               BEGIN
#               -- Remove the coalesce and the update will work.
#               -- Remove the multiplication and the update will work.
#               -- Remove this unneeded variable and the update will work.
#               NewHours = coalesce(new.new_field * (0), 0);
#               
#               -- Remove this exit command and the update will work. I know it's not needed,
#               -- however in the scenario I ran into this there was much more code after the
#               -- exit, and the exit was inside an IF clause. This is just the simplest way of reproducing it.
#               exit;
#               end
#               ^
#               
#               -- Now update the record to see the error:
#               update new_table set new_field = 6;
# tracker_id:   CORE-2811
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE NEW_TABLE (
    NEW_FIELD NUMERIC(9,2)
);

INSERT INTO NEW_TABLE (NEW_FIELD) VALUES (4);

SET TERM ^ ;

CREATE OR ALTER TRIGGER NEW_TRIGGER FOR NEW_TABLE
ACTIVE AFTER UPDATE POSITION 20
AS
declare variable NewHours numeric(9,2) = 0;
BEGIN
NewHours = coalesce(new.new_field * (0), 0);
exit;
end
^
"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """update new_table set new_field = 6;
select new_field from new_table;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
   NEW_FIELD
============
        6.00

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

