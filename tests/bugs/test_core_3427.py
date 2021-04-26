#coding:utf-8
#
# id:           bugs.core_3427
# title:        Server crashing with UTF8 blobs
# decription:   
# tracker_id:   CORE-3427
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table tbl (blob_field blob sub_type text character set utf8 collate unicode_ci_ai);
    -- See ticket: seems that this crash depended on concrete data, so it was decided to copy these text from ticket:
    insert into tbl values ('крупнейший европейский журнал о компьютерах. Вышел на рынок компьютерных изданий с уникальной концепцией и предназначен для людей, которые интересуются компьютерами, Интернетом, средствами телекоммуникаций, аудио-, видео- и фототехникой. Каждые две недели читателям предлагаются новости индустрии, тесты оборудования и программ, обучающие курсы и практические советы. Издание интересно как новичкам, так и опытным пользователям.');
    commit;
    -- Confirmed crash on 2.5.0, fine on 2.5.1 and later (02.04.2015):
    set list on;
    select count(*)  cnt
    from tbl 
    where blob_field like '%test%';   
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CNT                             0 
  """

@pytest.mark.version('>=2.5.1')
def test_core_3427_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

