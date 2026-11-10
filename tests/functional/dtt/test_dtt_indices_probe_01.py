#coding:utf-8

"""
ID:          functional.dtt.test_dtt_indices_probe_01
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9130
TITLE:       Index support for Declared LTT - basic test.
DESCRIPTION:
NOTES:
    Original commit:
        https://github.com/FirebirdSQL/firebird/commit/f93b6ce7ba148e6185c40a3328ca56686626e2ae

    [31.08.2026] pzotov
"""
import time
from pathlib import Path
import locale
import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation, DatabaseError

db = db_factory()
act = python_act('db')
tmp_sql = temp_file('tmp_dtt_indices.sql')
tmp_log = temp_file('tmp_dtt_indices.log')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, tmp_log: Path, capsys):

    with act.db.connect(charset = 'utf8') as con:
        cur = con.cursor()

        # 1. Check ability to create index for every known Firebird data types except blobs:
        # Examples from gh_8950_test.py:
        # ------------------------------
        types_map = {
            't_boo' : ('boolean'                  , ( 'false', 'true' ) ) # see README.packages.txt: "2) Bool As Value"
           ,'t_sml' : ('smallint'                 , ( '-32768', '32767' ) )
           ,'t_int' : ('int'                      , ( '-2147483648', '2147483647' ) )
           ,'t_big' : ('bigint'                   , ( '-9223372036854775808', '9223372036854775807' ) )
           ,'t_128' : ('int128'                   , ( '-170141183460469231731687303715884105728', '170141183460469231731687303715884105727' ) )
           ,'t_flt' : ('float'                    , ( '3.40282346638e38', '1.40129846432e-45', '1.17549435082e-38' ) )
           ,'t_dbl' : ('double precision'         , ( '-3e-308', '3e-308', '1.7976931348623157e308', '-9007199254740992', '9007199254740992' ) ) # NOT YET ALLOWED, see gh-8647: '4.9406564584124e-324', '2.2250738585072009e-308',
           ,'t_num' : ('numeric(2,2)'             , ( '-327.68', '327.67' ) )
           ,'t_dec' : ('decimal(2,2)'             , ( '-327.68', '327.67' ) )
           ,'t_dfl' : ('decfloat'                 , ( '-9.999999999999999999999999999999999E6144', '-1.0E-6143', '1.0E-6143', '9.999999999999999999999999999999999E6144', '0E-6144' ) )
           ,'t_dat' : ('date'                     , ( "'29.02.2004'", ) )
           ,'t_tim' : ('time'                     , ( "'01:02:03.456'", ) )
           ,'t_tms' : ('timestamp'                , ( "'29.02.2004 01:02:03.456'", ) )
           ,'t_tmz' : ('time with time zone'      , ( "'01:02:03.456 Indian/Cocos'", ) )
           ,'t_tsz' : ('timestamp with time zone' , ( "'29.02.2004 01:02:03.456 Indian/Cocos'", ) )
           ,'t_utf8_regular'    : ('varchar(255) character set utf8',  ("'შობას გილოცავთ'",) )         # georgian // UnicodeDecodeError: 'charmap' codec can't decode byte 0x98 in position 24606: character maps to <undefined>
           #,'t_utf8_regular'    : ('varchar(255) character set utf8',  ("'მადლობა'",) )
           ,'t_utf8_ci_ai'      : ('varchar(255) character set utf8 collate unicode_ci_ai',  ("'Շնորհավոր Սուրբ Ծնունդ'",) ) # armenian
           ,'t_iso8859_1_da_da' : ('varchar(255) character set iso8859_1 collate da_da',  ("q'#Børn får søde gærøl#'",)  )
           ,'t_iso8859_1_de_de' : ('varchar(255) character set iso8859_1 collate de_de',  ("q'#Müßiggänger müssen süße Äpfel grüßen#'",)  )
           ,'t_iso8859_1_fr_fr' : ('varchar(255) character set iso8859_1 collate fr_fr',  ("q'#L'été, là-bas, ç'a été délicieux#'",)  )
        }

        ddl_common = [
            'set bail off;'
            ,'set list on;'
            ,'set autoterm on;'
            ,"create exception exc_record_not_found 'Table @1 not found record with value [@2] of type `@3`';"
            ,'set explain on;'
        ]
        for k, v in types_map.items():
            decl_type = v[0]
            check_lst = v[1]
            for idx_dir in ('ascending', 'descending'):
                ddl_common.extend(
                    [   
                        'execute block returns(exc_gdscode int, exc_message varchar(8190)) as'
                        ,f'    declare v_chk {decl_type};'
                        ,f'    declare temporary table {k}_{idx_dir}( {k} {decl_type} ) UNIQUE {idx_dir} index idx_{k}_{idx_dir[:3]} ( {k} );'
                        ,f'begin'
                    ]
                )
                for x in check_lst:
                    ddl_common.extend(
                        [
                             f'    v_chk = {x};'
                            ,f'    insert into {k}_{idx_dir}( {k} ) values( :v_chk );'
                            ,f'    if ( (select count(*) from {k}_{idx_dir} where {k} = :v_chk) is distinct from 1) then'
                            ,f'    begin'
                            ,f"        exception exc_record_not_found using('{k}_{idx_dir}', {x}, '{decl_type}');"
                            ,f'    end'
                        ]
                    )
                    if x == check_lst[-1]:
                        # Here we check that index is actually UNIQUE: attempt to insert duplicate must fail.
                        ddl_common.extend(
                            [
                                 f'    v_chk = {x};'
                                ,f'    insert into {k}_{idx_dir}( {k} ) values( :v_chk );'
                                ,f'    when any do'
                                ,f'    begin'
                                ,f'        exc_gdscode = gdscode;'
                                ,f'        exc_message = ascii_char(10) || rdb$error(message);'
                                ,f'        suspend;'
                                ,f'    end'
                            ]
                        )
                        
                ddl_common.append('end;')

        #print('\n'.join(ddl_common))
    #
    # --==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++

    tmp_sql.write_text('\n'.join(ddl_common), encoding = 'utf-8')

    act.expected_stdout = f"""
    """
    act.isql(switches=['-q'], charset = 'utf8', combine_output = True, input_file = tmp_sql, io_enc = locale.getpreferredencoding())
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()


    #act.stdout = capsys.readouterr().out
    #assert act.clean_stdout == act.clean_expected_stdout
    #act.reset()
