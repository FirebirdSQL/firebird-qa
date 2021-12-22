#coding:utf-8
#
# id:           bugs.core_6137
# title:        Server crashes when it run SQL
# decription:   
#                   Confirmed bug on: 4.0.0.1573, 3.0.5.33166
#                   (got in firebird.log: "internal Firebird consistency check (invalid SEND request (167), file: JrdStatement.cpp line: 327)")
#               
#                   Checked on: 4.0.0.1575: OK, 1.834s; 3.0.5.33168: OK, 0.916s.
#                   Checked on: 2.5.9.27142 (10.09.2019), but previous snapshot 2.5.9.27139 (03.06.2019) also worked fine - without bugcheck.
#                
# tracker_id:   CORE-6137
# min_versions: ['2.5.9']
# versions:     2.5.9
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.9
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table tmp_labelbarcode ( 
        id integer not null, 
        barcode char(20) not null, 
        idlabel integer not null 
    ); 

    alter table tmp_labelbarcode add primary key (id); 
    create index tmlb_barcode on tmp_labelbarcode (barcode); 
    create index tmlb_idlabel on tmp_labelbarcode (idlabel); 
    create unique index tmp_labelbarcode_idx1 on tmp_labelbarcode (barcode, idlabel); 
    commit;

    insert into tmp_labelbarcode (id, barcode, idlabel) values (224423, '4627136039368', 278164); 
    commit;

    set count on;
    --set echo on;

    select tmp_labelbarcode.BARCODE 
    from tmp_labelbarcode 
    where tmp_labelbarcode.BARCODE = '462713603936820000004620016596753'
    order by tmp_labelbarcode.BARCODE 
    ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
"""

@pytest.mark.version('>=2.5.9')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

