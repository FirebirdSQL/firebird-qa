#coding:utf-8
#
# id:           bugs.core_3210
# title:        The cursor identified in the UPDATE or DELETE statement is not positioned on a row. no current record for fetch operation in SELECT query
# decription:   
# tracker_id:   CORE-3210
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core3210.fbk', init=init_script_1)

test_script_1 = """
    set list on;
    select count(*) cnt
    from (
        select
        depozit.number || ' ' ||
        coalesce(
                    iif(
                        nast.bul_id is not null
                        , coalesce(bulgarians.name,'') || ' ' || coalesce(bulgarians.family,'')
                        , coalesce(foreigners.name_cyr,foreigners.name_lat)
                    )
                ,''
                ) as name
        from
            depozit left join nast on nast.id = depozit.nast_id
            left join bulgarians on bulgarians.id = nast.bul_id
            left join foreigners on foreigners.id = nast.for_id
        order by 1 --- ==> no current record for fetch operation
    );
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CNT                             171
"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

