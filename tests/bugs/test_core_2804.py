#coding:utf-8
#
# id:           bugs.core_2804
# title:        Problems with COMMENT ON and strings using introducer (charset)
# decription:   
# tracker_id:   CORE-2804
# min_versions: ['2.5.4']
# versions:     2.5.4
# qmid:         bugs.core_2804

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.4
# resources: None

substitutions_1 = [('DESCR_BLOB_ID.*', '')]

init_script_1 = """"""

db_1 = db_factory(from_backup='core2804-ods11.fbk', init=init_script_1)

test_script_1 = """
    -- Database was prepared with following statements:
    -- recreate table test1(id int);
    -- recreate table test2(id int);
    -- commit;
    -- comment on table test1 is _win1251 'win1251: <cyrillic text here encoded with win1251>';
    -- comment on table test2 is _unicode_fss 'unicode_fss: <cyrillic text here encoded with UTF8>';
    -- commit;

    set blob all;
    set list on;
    select r.rdb$description as descr_blob_id
    from rdb$relations r where r.rdb$relation_name in ( upper('test1'), upper('test2') )
    order by r.rdb$relation_name;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    DESCR_BLOB_ID                   0:3
    win1251: Протокол собрания об уплотнении квартир дома

    DESCR_BLOB_ID                   0:6
    unicode_fss: Протокол собрания о помощи детям Германии  
  """

@pytest.mark.version('>=2.5.4')
def test_core_2804_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

