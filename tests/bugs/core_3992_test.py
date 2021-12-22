#coding:utf-8
#
# id:           bugs.core_3992
# title:        No records in the table rdb$dependencies for ddl trigger
# decription:   
# tracker_id:   CORE-3992
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
    recreate table ddl_log (
        id integer,
        ddl_event varchar(25),
        sql blob sub_type text
    );
    
    set term ^;
    create or alter trigger ddl_log_trigger after any ddl statement
    as
    begin
      insert into ddl_log(sql, ddl_event)
        values (rdb$get_context('DDL_TRIGGER', 'SQL_TEXT'),
                rdb$get_context('DDL_TRIGGER', 'DDL_EVENT') );
    end
    ^
    set term ;^
    commit;
    
    set list on;
    
    select sign(count(*)) "is_any_rows_there ?"
    from rdb$dependencies d
    where upper('ddl_log_trigger') in (d.rdb$dependent_name, d.rdb$depended_on_name);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    is_any_rows_there ?             1
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

