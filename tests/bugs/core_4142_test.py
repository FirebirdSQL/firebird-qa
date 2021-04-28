#coding:utf-8
#
# id:           bugs.core_4142
# title:        Regression: Server crashes while preparing a query with DISTINCT and ORDER BY
# decription:   
# tracker_id:   CORE-4142
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """
    recreate table trel(id smallint, name char(31) character set unicode_fss collate unicode_fss);
    commit;
    insert into trel(id, name) select row_number()over(), 'RDB$NAME_' || row_number()over()
    from rdb$types
    rows 9;
    commit;
    alter table trel add constraint trel_name_unq unique (name);
    create index trel_id on trel(id);
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    select distinct id + 0 id, name
    from trel
    order by name;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID NAME
    == ==========
     1 RDB$NAME_1
     2 RDB$NAME_2
     3 RDB$NAME_3
     4 RDB$NAME_4
     5 RDB$NAME_5
     6 RDB$NAME_6
     7 RDB$NAME_7
     8 RDB$NAME_8
     9 RDB$NAME_9
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

