#coding:utf-8
#
# id:           bugs.core_3245
# title:        SUBSTRING on long blobs truncates result to 32767 if third argument not present
# decription:
# tracker_id:   CORE-3245
# min_versions: ['2.1.5']
# versions:     2.1.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.5
# resources: None

substitutions_1 = [('blob_.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    with q (s) as (
        select cast(cast('abc' as char(32767)) as blob sub_type text)
                 || cast('def' as char(32767))
                 || cast('ghi' as char(32767))
                 || 'tail'
        from rdb$database
    )
    ,r (sub_for, sub_nofor) as (
        select substring(s from 8000 for 120000),
                    substring(s from 8000)
        from q
    )
    select
      char_length(s) as "char_length(s)"
      ,right(s, 3) as "blob_right(s,3)"
      ,char_length(sub_for) as "char_length(sub_for)"
      ,right(sub_for, 3) as "blob_right(sub_for, 3)"
      ,char_length(sub_nofor) as "char_length(sub_nofor)"
      ,right(sub_nofor, 3) as "blob_right(sub_nofor, 3)"
    from q cross join r
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    char_length(s)                  98305
    ail
    char_length(sub_for)            90306
    ail
    char_length(sub_nofor)          90306
    ail
  """

@pytest.mark.version('>=2.1.5')
def test_1(act_1: Action):
    act_1.db.set_async_write()
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

