#coding:utf-8

"""
ID:          issue-5515
ISSUE:       5515
TITLE:       IN/ANY/ALL predicates may cause sub-optimal (late filtering) execution of joins
DESCRIPTION:
    Plan BEFORE fix was (confirmed on 4.0.0.258):
        ...
        Select Expression
            -> Filter
                -> Nested Loop Join (inner)          <<<<<<<  no filter of "DP_REGISTRO" table
                    -> Table "DP_REGISTRO" Full Scan <<<<<<<  after it was scanned
                    -> Filter
                        -> Table "DP_RECIBO" Access By ID
                            -> Bitmap
                                -> Index "UNQ1_DP_RECIBO" Range Scan (partial match: 1/2)

    Plan AFTER fix (confirmed on 4.0.0.313):
        ...
        Select Expression
            -> Nested Loop Join (inner)
                -> Filter  <<<<<<<<<<<<<<<<<<<<<<<<<<<  EARLY FILTERING MUST BE HERE <<<<<
                    -> Table "DP_REGISTRO" Full Scan
                -> Filter
                    -> Table "DP_RECIBO" Access By ID
                        -> Bitmap
                            -> Index "UNQ1_DP_RECIBO" Range Scan (partial match: 1/2)
JIRA:        CORE-5236
FBTEST:      bugs.core_5236
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table dp_registro_oest(
        autoinc_registro int primary key using index pk_dp_registro_oest,
        registro_pri_roest integer not null,
        registro_sec_roest integer not null
    );

    recreate table dp_recibo(
        codigo_rec bigint primary key,
        registro_rec integer not null,
        competencia_rec varchar(6) not null,
        unique(registro_rec, competencia_rec) using index unq1_dp_recibo
    );

    recreate table  dp_registro(
        autoinc_registro integer primary key using index pk_dp_registro
    );


    alter table dp_registro_oest
        add constraint fk_dp_registro_oest_1 foreign key (registro_pri_roest)
            references dp_registro (autoinc_registro) on update cascade
        ,add constraint fk_dp_registro_oest_2 foreign key (registro_sec_roest)
            references dp_registro (autoinc_registro) on update cascade
        ,add constraint unq1_dp_registro_oest unique (registro_pri_roest, registro_sec_roest)
    ;
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set explain on;
    select 1
    from dp_recibo
    inner join dp_registro on dp_registro.autoinc_registro = dp_recibo.registro_rec
    where
      dp_registro.autoinc_registro in (
        select registro_sec_roest
        from dp_registro_oest
        where registro_pri_roest = 1
      )
    ;

"""

act = isql_act('db', test_script)

fb3x_expected_out = """
    Select Expression
        -> Filter
            -> Filter
                -> Table "DP_REGISTRO_OEST" Access By ID
                    -> Bitmap
                        -> Index "UNQ1_DP_REGISTRO_OEST" Unique Scan
    Select Expression
        -> Nested Loop Join (inner)
            -> Filter
                -> Table "DP_REGISTRO" Full Scan
            -> Filter
                -> Table "DP_RECIBO" Access By ID
                    -> Bitmap
                        -> Index "UNQ1_DP_RECIBO" Range Scan (partial match: 1/2)
"""

fb5x_expected_out = """
    Sub-query
        -> Filter
            -> Filter
                -> Table "DP_REGISTRO_OEST" Access By ID
                    -> Bitmap
                        -> Index "UNQ1_DP_REGISTRO_OEST" Unique Scan
    Select Expression
        -> Filter
            -> Hash Join (inner)
                -> Table "DP_RECIBO" Full Scan
                -> Record Buffer (record length: 25)
                    -> Filter
                        -> Table "DP_REGISTRO" Full Scan
"""

@pytest.mark.version('>=3.0.1')
def test_1(act: Action):
    act.expected_stdout = fb3x_expected_out if act.is_version('<5') else fb5x_expected_out
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
