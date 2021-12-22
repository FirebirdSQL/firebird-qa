#coding:utf-8
#
# id:           bugs.core_5421
# title:        Performance degradation in FB 3.0.2 compared to FB 2.5.7
# decription:   
#                  Confirmed inefficient plan on 3.0.2.32644, 4.0.0.477: 
#                  PLAN JOIN (D ORDER C5421_TDETL_DTS, C INDEX (C5421_TMAIN_ID, C5421_TMAIN_EKEY))
#               
#                  All fine on 3.0.2.32658, WI-T4.0.0.483
#                
# tracker_id:   CORE-5421
# min_versions: ['2.5.7']
# versions:     2.5.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table tmain(id int, ekey int);
    recreate table tdetl(doc_id int, dts timestamp); 

    set term ^;
    execute block as
      declare n int = 10000; -- 7600000;
      declare d int = 100; -- 5000;
      declare i int = 0;
    begin
      while ( i < n ) do
      begin
        insert into tdetl(doc_id, dts) values( :i, current_date-rand()*:d )
        returning :i+1 into i;
      end
      insert into tmain(id, ekey) values(0, 100);
    end^
    set term ;^
    commit;

    create index c5421_tmain_id on tmain(id);
    create index c5421_tmain_ekey on tmain(ekey);

    create index c5421_tdetl_doc_id on tdetl(doc_id);
    create descending index c5421_tdetl_dts on tdetl(dts);
    commit;

    --set width rel_name 8;
    --set width idx_name 30;
    --select ri.rdb$relation_name rel_name, ri.rdb$index_name idx_name, ri.rdb$statistics
    --from rdb$indices ri where ri.rdb$index_name starting with 'C5421';

    set list on;
    set plan on;
    --set stat on;
    set count on;
    select first 1 d.doc_id --, d.dts 
    from tmain c 
    join tdetl d ON d.doc_id = c.id
    where
        c.ekey = 100 and
        d.dts <= 'tomorrow'
    order by
        d.dts desc
    ;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN SORT (JOIN (C INDEX (C5421_TMAIN_EKEY), D INDEX (C5421_TDETL_DOC_ID)))
    DOC_ID                          0
    Records affected: 1
"""

@pytest.mark.version('>=2.5.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

