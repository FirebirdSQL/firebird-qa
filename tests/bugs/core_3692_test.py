#coding:utf-8

"""
ID:          issue-4040
ISSUE:       4040
TITLE:       Cannot drop a NOT NULL constraint on a field participating in the UNIQUE constraint
DESCRIPTION:
JIRA:        CORE-3692
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table cset (cname varchar(250) character set none not null);
    commit;
    alter table cset add constraint uq_cset unique (cname);
    commit;
"""

db = db_factory(init=init_script)

test_script = """
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

act = isql_act('db', test_script)

expected_stdout = """
CNAME                           VARCHAR(250) Not Null
CONSTRAINT UQ_CSET:
  Unique key (CNAME)
CNAME                           VARCHAR(250) Nullable
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

