#coding:utf-8
#
# id:           bugs.core_3964
# title:        It is not possible to create a ddl-trigger with "any DDL statement" clause
# decription:   
# tracker_id:   CORE-3964
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
    create table mp$modified_tables (relation_name char(31));
    commit;
    create index mp$modified_tables_idx on mp$modified_tables (relation_name);
    commit;
    
    set term ^;
    create trigger taa_sql1
    active after any ddl statement position 0 as
    begin
        if (
            rdb$get_context('DDL_TRIGGER', 'OBJECT_TYPE') = 'TABLE'
            and
            (
                rdb$get_context('DDL_TRIGGER', 'EVENT_TYPE') in ('CREATE', 'DROP')
                or
                rdb$get_context('DDL_TRIGGER', 'SQL_SOURCE') containing 'FIELD'
            )
        ) then
            insert into mp$modified_tables (relation_name)
            values (rdb$get_context('DDL_TRIGGER', 'OBJECT_NAME'));
    end
    ^
    set term ;^
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_core_3964_1(act_1: Action):
    act_1.execute()

