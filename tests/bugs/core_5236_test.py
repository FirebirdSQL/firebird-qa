#coding:utf-8

"""
ID:          issue-5515
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/5515
TITLE:       IN/ANY/ALL predicates may cause sub-optimal (late filtering) execution of joins
DESCRIPTION:
    Plan BEFORE fix was (confirmed on 4.0.0.258):
        ...
        Select Expression
            -> Filter
                -> Nested Loop Join (inner)          <<<<<<<  no filter of "DP_REGISTRO" table
                    -> Table "DP_REGISTRO" Full Scan <<<<<<<  after it was scanned
                    -> Filter
                        ...
    Plan AFTER fix (confirmed on 4.0.0.313):
        ...
        Select Expression
            -> Nested Loop Join (inner)
                -> Filter  <<<<<<<<<<<<<<<<<<<<<<<<<<<  EARLY FILTERING MUST BE HERE <<<<<
                    -> Table "DP_REGISTRO" Full Scan
                -> Filter
                    ...
JIRA:        CORE-5236
FBTEST:      bugs.core_5236
NOTES:
    [16.06.2024] pzotov
    Plan for FB 5.x and 6.x changed since 28-may-2024, build 6.0.0.363 #95442.
    It was adjusted after talk with dimitr: must be the same for all FB versions
    (with only difference: 'Sub-query' at the top line for FB 5.x+).
    Changed filler character for show padding ('#' --> '.').

    [23.03.2025] pzotov
    Separated expected_out because plans differ on 6.x vs previous versions since commit fc12c0ef
    ("Unnest IN/ANY/EXISTS subqueries and optimize them using semi-join algorithm (#8061)").
    Checked on 6.0.0.687-730aa8f; 5.0.3.1633-25a0817 
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

act = python_act('db')

#-----------------------------------------------------------

def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped

#-----------------------------------------------------------

@pytest.mark.version('>=3.0.1')
def test_1(act: Action, capsys):

    test_sql = """
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

    fb4x_expected_out = """
        Select Expression
        ....-> Filter
        ........-> Filter
        ............-> Table "DP_REGISTRO_OEST" Access By ID
        ................-> Bitmap
        ....................-> Index "UNQ1_DP_REGISTRO_OEST" Unique Scan
        Select Expression
        ....-> Nested Loop Join (inner)
        ........-> Filter
        ............-> Table "DP_REGISTRO" Full Scan
        ........-> Filter
        ............-> Table "DP_RECIBO" Access By ID
        ................-> Bitmap
        ....................-> Index "UNQ1_DP_RECIBO" Range Scan (partial match: 1/2)
    """

    fb5x_expected_out = """
        Sub-query
        ....-> Filter
        ........-> Filter
        ............-> Table "DP_REGISTRO_OEST" Access By ID
        ................-> Bitmap
        ....................-> Index "UNQ1_DP_REGISTRO_OEST" Unique Scan
        Select Expression
        ....-> Nested Loop Join (inner)
        ........-> Filter
        ............-> Table "DP_REGISTRO" Full Scan
        ........-> Filter
        ............-> Table "DP_RECIBO" Access By ID
        ................-> Bitmap
        ....................-> Index "UNQ1_DP_RECIBO" Range Scan (partial match: 1/2)
    """

    fb6x_expected_out = """
        Select Expression
        ....-> Nested Loop Join (semi)
        ........-> Nested Loop Join (inner)
        ............-> Table "DP_REGISTRO" Full Scan
        ............-> Filter
        ................-> Table "DP_RECIBO" Access By ID
        ....................-> Bitmap
        ........................-> Index "UNQ1_DP_RECIBO" Range Scan (partial match: 1/2)
        ........-> Filter
        ............-> Table "DP_REGISTRO_OEST" Access By ID
        ................-> Bitmap
    """

    with act.db.connect() as con:
        cur = con.cursor()
        ps = cur.prepare(test_sql)
        print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

    act.expected_stdout = fb4x_expected_out if act.is_version('<5') else fb5x_expected_out if act.is_version('<6') else fb6x_expected_out
    act.execute(combine_output = True)
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout

