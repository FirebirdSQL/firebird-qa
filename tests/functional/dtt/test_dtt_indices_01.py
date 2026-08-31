#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/9130
TITLE:       Index support for Declared LTT - basic test.
DESCRIPTION:
    Test iterates on list of datatypes <T> and for each <T> creates TWO execute blocks with returning values:
        * first EB declares temporary PSQL table with single field of <T> and unique ASCENDING index on this column;
        * second EB does the same but with DESCENDING index.
    The body of each EB is the same:
        * we try to insert several unique values and check for each of them that it can be found using appropriate index;
        * we try to insert duplicate (using last inserted value again) and check that expected exception will raise.
          Info related to this exception (gdscode and message) is returned from EB (335544349 "attempt to store duplicate...")
    On each iteration test increments the list of lines which must present in the final output (both for explained plans and
    error messages) -- see 'all_output_lines'.
    Result of '\n'.join(all_output_lines) must be equal to the content of capsys.readouterr().out.
NOTES:
    1. OFFTOP.
       Initial version of this test tried to create .sql file (encoded in utf8) and run act.isql() with parameters:
           charset = 'utf8', combine_output = True, input_file = tmp_sql, io_enc = locale.getpreferredencoding()
       Unfortunately, this attempt failed while handling data in Geogian language with UnicodeDecodeError
       For example, an attempt to use 'შობას გილოცავთ' (~Merry Christmas) or 'დიდი' (~Big) raised such error
       ('charmap' codec can't decode byte ... in position ...: character maps to <undefined>).
       Same occurred if DTT is replace4d with GTT.
       No such problem occurred with text in Armenian. The reason remains currently unknown. To be investigated later.

    2. The phrase 'Problematic key value is ...' (in the exception related to attempt tom store duplicate key) will contain
       value in its right part that is result of cast source value to varchar type.
       In order to avoid unnecessary complications of code, it was decided to exclude this value from comparison.
    
    Original commit:
        https://github.com/FirebirdSQL/firebird/commit/f93b6ce7ba148e6185c40a3328ca56686626e2ae

    [31.08.2026] pzotov
    Checked on 20260829_024127-6.0.0.2164-2d371e2.
"""
import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory(init = "create exception exc_record_not_found 'Table @1 not found record with value [@2] of type `@3`';")

substitutions = [
     (r'Sub-query \(line \d+, column \d+\)', 'Sub-query (line N, column M)')
    ,(r'(")?RDB\$PSQL_LTT_\d+(")?', 'RDB_PSQL_LTT')
    ,('Problematic key value is.*', 'Problematic key value is')
    ,(r'(-)?At block line: \d+, col: \d+', 'At block line: X, col: Y')
]

act = python_act('db', substitutions = substitutions)
#-----------------------------------------------------------
def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped
#-----------------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

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
       # georgian // ACHTUNG. UnicodeDecodeError: 'charmap' codec can't decode byte 0x98 in position 24606: character maps to <undefined>
       #,'t_utf8_regular'    : ('varchar(255) character set utf8',  ("'შობას გილოცავთ'",) )
       #,'t_utf8_regular'    : ('varchar(255) character set utf8',  ("'დიდი'",) )
       ,'t_utf8_regular'    : ('varchar(255) character set utf8',  ("'მადლობა'",) )
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

    with act.db.connect(charset = 'utf-8') as con:
        cur = con.cursor()
        
        all_output_lines = []

        for k, v in types_map.items():
            decl_type = v[0]
            check_lst = v[1]
            for idx_dir in ('ascending', 'descending'):

                ddl_common = []
                explained_plan_lines = []
                exe_block_data_lines = []
                dtt_index_name = f'idx_{k}_{idx_dir[:3]}'.upper()

                ddl_common.extend(
                    [   
                        'execute block returns(exc_gdscode int, exc_message varchar(8190)) as'
                        ,f'    declare v_chk {decl_type};'
                        ,f'    declare temporary table {k}_{idx_dir}( {k} {decl_type} ) UNIQUE {idx_dir} index {dtt_index_name} ( {k} );'
                        ,f'begin'
                    ]
                )
                for x in check_lst:
                    ddl_common.extend(
                        [
                             f'    v_chk = {x};'
                            ,f'    insert into {k}_{idx_dir}( {k} ) values( :v_chk );'
                            # this must cause appearance of 'Index "..." Unique Scan' in the explained plan:
                            ,f'    if ( (select count(*) from {k}_{idx_dir} where {k} = :v_chk) is distinct from 1) then'
                            ,f'    begin'
                            ,f"        exception exc_record_not_found using('{k}_{idx_dir}', {x}, '{decl_type}');"
                            ,f'    end'
                        ]
                    )

                    explained_plan_lines.extend(
                        [
                             'Sub-query (line 111, column 222)'
                            ,'....-> Singularity Check'
                            ,'........-> Aggregate'
                            ,'............-> Filter'
                            ,'................-> Table "RDB$PSQL_LTT_0" Access By ID'
                            ,'....................-> Bitmap'
                            ,f'........................-> Index "{dtt_index_name}" Unique Scan'
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
                                ,f"        exc_message = ascii_char(10) || rdb$error(message);"
                                ,f'        suspend;'
                                ,f'    end'
                            ]
                        )
                        exe_block_data_lines.extend(
                            [
                                 f'EXC_GDSCODE : 335544349'
                                ,f'EXC_MESSAGE :'
                                ,f'attempt to store duplicate value (visible to active transactions) in unique index "{dtt_index_name}"'
                                ,f'Problematic key value is' # do NOT add here ("{k.upper()}" = ...) - its output may depend on OS and datatype.
                                ,f'At block line: 333, col: 444'
                            ]
                        )
                        
                ddl_common.append('end;')

                ps, rs = None, None
                try:
                    ps = cur.prepare('\n'.join(ddl_common) )
                    # Print explained plan with padding eash line by dots in order to see indentations:
                    print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

                    # ::: NB ::: 'ps' returns data, i.e. this is SELECTABLE expression.
                    # We have to store result of cur.execute(<psInstance>) in order to
                    # close it explicitly.
                    # Otherwise AV can occur during Python garbage collection and this
                    # causes pytest to hang on its final point.
                    # Explained by hvlad, email 26.10.24 17:42
                    rs = cur.execute(ps)
                    cur_cols = cur.description
                    for r in rs:
                        for i in range(0,len(cur_cols)):
                            print( cur_cols[i][0], ':', r[i] )
                except DatabaseError as e:
                    print(e.__str__())
                    print(e.gds_codes)
                finally:
                    if rs:
                        rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                    if ps:
                        ps.free()
                
                all_output_lines.extend(explained_plan_lines)
                all_output_lines.extend(exe_block_data_lines)

            #< for idx_dir in ('ascending', 'descending')
        #< for k, v in types_map.items()
    # < with act.db.connect(charset = 'utf-8') as con

    # --==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++

    act.expected_stdout = '\n'.join(all_output_lines)
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
