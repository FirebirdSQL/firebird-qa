#coding:utf-8
#
# id:           bugs.core_3692
# title:        Cannot drop a NOT NULL constraint on a field participating in the UNIQUE constraint
# decription:   
# tracker_id:   CORE-3692
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table cset (cname varchar(250) character set none not null); 
    commit; 
    alter table cset add constraint uq_cset unique (cname); 
    commit; 
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
show table cset;
    
    set term ^;
    execute block as
      declare v_stt varchar(70);
    begin
        for
            with
            inp as(select 'cset' nm from rdb$database)
            ,pk_defs as( -- obtain PK constraint and get fields that assembles it
              select
                rc.rdb$relation_name rel_name
                ,rc.rdb$constraint_name pk_name
                ,rc.rdb$index_name pk_idx
                ,rs.rdb$field_name fld_name
                ,rs.rdb$field_position fld_pos
              from rdb$relation_constraints rc
              join rdb$index_segments rs on rc.rdb$index_name=rs.rdb$index_name
              join inp i on rc.rdb$relation_name containing i.nm
              where rc.rdb$constraint_type containing 'PRIMARY'
            )
            -- select * from pk_defs
            ,chk_list as(
              select
                rc.rdb$relation_name rel_name
                ,rc.rdb$constraint_name sub_name
                ,rc.rdb$constraint_type sub_type
                ,'alter table '||trim(rc.rdb$relation_name)||' drop constraint '||trim(rc.rdb$constraint_name)||'; -- '||trim(rc.rdb$constraint_type) stt
                ,ck.rdb$trigger_name
                ,p.pk_name -- not null ==> field is included in PK, skip it
                ,decode(rc.rdb$constraint_type, 'UNIQUE', 99, 0) sort_weitgh
              from rdb$relation_constraints rc
              join inp i on rc.rdb$relation_name containing i.nm
              left join rdb$check_constraints ck on rc.rdb$constraint_name=ck.rdb$constraint_name
              left join pk_defs p on rc.rdb$relation_name=p.rel_name and ck.rdb$trigger_name=p.fld_name
              where
                rc.rdb$relation_name not like 'RDB$%'
                and rc.rdb$relation_name not like 'MON$%'
                and rc.rdb$relation_name not like 'IBE$%'
                and rc.rdb$constraint_type not containing 'PRIMARY'
                and p.pk_name is null -- ==> this field is NOT included in PK constraint
                order by rc.rdb$relation_name, decode(rc.rdb$constraint_type, 'UNIQUE', 99, 0)
            )
            select cast(stt as varchar(70)) stt from chk_list
            into v_stt
        do begin
            execute statement (v_stt);
        end
      
    end
    ^ set term ;^
    commit;
    
    show table cset;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
CNAME                           VARCHAR(250) Not Null 
CONSTRAINT UQ_CSET:
  Unique key (CNAME)
CNAME                           VARCHAR(250) Nullable 
"""

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

