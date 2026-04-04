#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8950
TITLE:       ALTER TABLE <T> ALTER <INDEXED_NON_TEXTUAL_COL> TYPE VARCHAR(nnnn) causes column to be non-updatable state
DESCRIPTION:
    Test verifies ability to convert a table column 'F01' (which has not-null values) from non-textual type to [var]char.
    This is done for every non-textual types, i.e. numeric (all), boolean and date/time/timestamp [with time zone].
    For each checked type three indices are created:
        * regular unique index on this column;
        * computed-by index with expression: (F01 || '')
        * conditional index on F01 but with requirement F01 is not null.
    Then we add several rows with not-null values and one record with null.
    After this we do 'alter table ... alter column F01 type [var]char(NNN)' where NNN must be sufficient for new values
    to be accomodated in this column.
    Finally, we try to insert into this column textual values which for sure can NOT be interpreted as any but string
    (i.e. can not be casted to old data type).
    We repeat this for utf8 and iso8859_1 charsets, using several collates for each of them and non-ascii symbols in data.
    No errors must occur during these steps.
NOTES:
    [04.04.2026] pzotov
    Confirmed bug on 6.0.0.1871-3ba5e48, got:
       * for all datatypes except DECFLOAT:
         Expression evaluation error for index <T_***_F01_UNQ> / conversion error from string (gds: 335545153, 335544334)
       * for DECFLOAT column:
         Expression evaluation error for index <T_***_F01_UNQ> / Decimal float invalid operation.  An indeterminant error...
         (gdscodes: 335545153, 335545141, 335544334).
    Checked on 6.0.0.1878-a877c7e.
"""
import time
from firebird.driver import DatabaseError

import pytest
from firebird.qa import *
db = db_factory()
act = python_act('db')

###################
TEXT_TYPE_LEN = 100
###################

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    types_map = {
        't_sml' : ('smallint'                 , ( '-32768', '32767' ) )
       ,'t_int' : ('int'                      , ( '-2147483648', '2147483647' ) )
       ,'t_big' : ('bigint'                   , ( '-9223372036854775808', '9223372036854775807' ) )
       ,'t_128' : ('int128'                   , ( '-170141183460469231731687303715884105728', '170141183460469231731687303715884105727' ) )
       ,'t_flt' : ('float'                    , ( '3.40282346638e38', '1.40129846432e-45', '1.17549435082e-38' ) )
       ,'t_dbl' : ('double precision'         , ( '-3e-308', '3e-308', '1.7976931348623157e308', '-9007199254740992', '9007199254740992' ) ) # NOT YET ALLOWED, see gh-8647: '4.9406564584124e-324', '2.2250738585072009e-308',
       ,'t_num' : ('numeric(2,2)'             , ( '-327.68', '327.67' ) )
       ,'t_dec' : ('decimal(2,2)'             , ( '-327.68', '327.67' ) )
       ,'t_dfl' : ('decfloat'                 , ( '-9.999999999999999999999999999999999E6144', '-1.0E-6143', '1.0E-6143', '9.999999999999999999999999999999999E6144', '0E-6144' ) )
       ,'t_boo' : ('boolean'                  , ( 'false', 'true' ) )
       ,'t_dat' : ('date'                     , ( '29.02.2004', ) )
       ,'t_tim' : ('time'                     , ( '01:02:03.456', ) )
       ,'t_tms' : ('timestamp'                , ( '29.02.2004 01:02:03.456', ) )
       ,'t_tmz' : ('time with time zone'      , ( '01:02:03.456 Indian/Cocos', ) )
       ,'t_tsz' : ('timestamp with time zone' , ( '29.02.2004 01:02:03.456 Indian/Cocos', ) )
    }

    charset_map = {
        'utf8'      :
           { ''              : 'შობას გილოცავთ',         # georgian
             'unicode_ci_ai' : 'Շնորհավոր Սուրբ Ծնունդ'  # armenian
           }
       ,'iso8859_1' :
           { 'da_da' : 'Børn får søde gærøl',
             'de_de' : 'Müßiggänger müssen süße Äpfel grüßen',
             'fr_fr' : "L'été, là-bas, ç'a été délicieux"
           }
    }

    for new_text_type in ('varchar', 'char'):
        for cset_chk_key, cset_chk_values in charset_map.items():
            for coll_name, text_for_check in cset_chk_values.items():
                collate_clause = ''
                if coll_name:
                    collate_clause = f' collate {coll_name}'

                with act.db.connect(charset = cset_chk_key) as con:
                    cur = con.cursor()
                    for k,v in types_map.items():
                        tmp_table_ddl = f'recreate table {k}( f01 {v[0]})'
                        con.execute_immediate(tmp_table_ddl)
                        con.commit()
                        con.execute_immediate(f'create unique index {k}_f01_unq on {k}(f01)')
                        con.execute_immediate(f"create index {k}_f01_expr on {k} computed by(f01 || '')")
                        con.execute_immediate(f'create index {k}_f01_cond on {k}(f01) where f01 is not null')
                        con.commit()
                        for p in v[1]:
                            cur.execute( f'insert into {k}(f01) values(?)', (p,) )
                        cur.execute( f'insert into {k}(f01) values(null)' )
                        con.commit()

                    for k in types_map.keys():
                        con.execute_immediate(f'alter table {k} alter f01 type {new_text_type}({TEXT_TYPE_LEN}) character set {cset_chk_key} {collate_clause}')
                        con.commit()

                with act.db.connect(charset = cset_chk_key) as con:
                    cur = con.cursor()
                    for k in types_map.keys():
                        try:
                            cur.execute( f'insert into {k}(f01) values(?)', (text_for_check,) )
                            con.commit()
                        except DatabaseError as e:
                            print(f"Could not insert data after 'ALTER <COL> to {new_text_type.upper()}({TEXT_TYPE_LEN}) character set {cset_chk_key.upper()} {collate_clause.upper()}'")
                            print(e.__str__())
                            print(e.gds_codes)
                        except Exception as x:
                            print(x)

    act.expected_stdout = """
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
