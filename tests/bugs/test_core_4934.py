#coding:utf-8
#
# id:           bugs.core_4934
# title:        Different collation ID for altered computed column
# decription:   
# tracker_id:   CORE-4934
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
    recreate table t_country(id int);
    commit;
    
    create or alter view v_test as
    select
         rf.rdb$relation_name rel_name
        ,rf.rdb$field_name fld_name
        --,rf.rdb$field_source fld_source
        ,f.rdb$character_set_id cset_id
        ,f.rdb$collation_id coll_id
    from rdb$relation_fields rf
    left join rdb$fields f on rf.rdb$field_source = f.rdb$field_name
    where rf.rdb$relation_name in( upper('t_country'), upper('t_translation_meta'))
    order by 1,2;
    
    commit;
    
    recreate table t_translation_meta (
        f_trm_id bigint not null,
        f_trm_code varchar(512) character set utf8 not null collate
        unicode_ci
    );
    commit;
    
    recreate table t_country (
        f_cnr_id bigint not null,
        f_trm_name_id bigint default -1 not null,
        cf_cnr_name computed by (
            (
                (
                    select f_trm_code
                    from t_translation_meta
                    where f_trm_id = f_trm_name_id
                )
            )
        )
    );
    commit;
    
    set width rel_name 20;
    set width fld_name 20;
    set width fld_source 20;
    
    set list on;
    
    select 'before' msg, v.* from v_test v;
    
    
    alter table t_country alter cf_cnr_name computed by
    (
        (
            (
                select
                f_trm_code
                from t_translation_meta
                where f_trm_id = f_trm_name_id
            )
        )
    );
    commit;
    
    select 'after' msg, v.* from v_test v;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             before
    REL_NAME                        T_COUNTRY                                                                                    
    FLD_NAME                        CF_CNR_NAME                                                                                  
    CSET_ID                         4
    COLL_ID                         3
    
    MSG                             before
    REL_NAME                        T_COUNTRY                                                                                    
    FLD_NAME                        F_CNR_ID                                                                                     
    CSET_ID                         <null>
    COLL_ID                         <null>
    
    MSG                             before
    REL_NAME                        T_COUNTRY                                                                                    
    FLD_NAME                        F_TRM_NAME_ID                                                                                
    CSET_ID                         <null>
    COLL_ID                         <null>
    
    MSG                             before
    REL_NAME                        T_TRANSLATION_META                                                                           
    FLD_NAME                        F_TRM_CODE                                                                                   
    CSET_ID                         4
    COLL_ID                         3
    
    MSG                             before
    REL_NAME                        T_TRANSLATION_META                                                                           
    FLD_NAME                        F_TRM_ID                                                                                     
    CSET_ID                         <null>
    COLL_ID                         <null>
    
    
    
    MSG                             after
    REL_NAME                        T_COUNTRY                                                                                    
    FLD_NAME                        CF_CNR_NAME                                                                                  
    CSET_ID                         4
    COLL_ID                         3
    
    MSG                             after
    REL_NAME                        T_COUNTRY                                                                                    
    FLD_NAME                        F_CNR_ID                                                                                     
    CSET_ID                         <null>
    COLL_ID                         <null>
    
    MSG                             after
    REL_NAME                        T_COUNTRY                                                                                    
    FLD_NAME                        F_TRM_NAME_ID                                                                                
    CSET_ID                         <null>
    COLL_ID                         <null>
    
    MSG                             after
    REL_NAME                        T_TRANSLATION_META                                                                           
    FLD_NAME                        F_TRM_CODE                                                                                   
    CSET_ID                         4
    COLL_ID                         3
    
    MSG                             after
    REL_NAME                        T_TRANSLATION_META                                                                           
    FLD_NAME                        F_TRM_ID                                                                                     
    CSET_ID                         <null>
    COLL_ID                         <null>
  """

@pytest.mark.version('>=3.0')
def test_core_4934_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

