#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/pull/8916
TITLE:       Package constants (#8916) - test for backup/restore.
DESCRIPTION:
    Test creates packages with constants of different types:
        * as literals belonging to every FB datatype (except arrays), with referring to them from packaged units;
        * as result of complex arithmetic expressions and query them further via SELECT;
        * as result call to some built-in functions (but all their input arguments must be constants).
    Also, we create temporary role and user, grant usage of these packages to the role and grant role to the user
    (just to check that 'GRANT USAGE' works for such packages).

    Then we extract metadata as .sql and store it into 'init_meta' veriable.
    After this we run backup and restore - no errors must occur for these actions (empty STDERR and retcode = 0).
    Finally, we extract metadata again and compare with 'init_meta'. No difference must exist between them.
NOTES:
    Original commit:
        https://github.com/FirebirdSQL/firebird/commit/7589a56aeffce8c529bcd8534803da1377da9f05
    Declaration of package constants as expressions// IIF(), NULLIF()
        https://groups.google.com/g/firebird-devel/c/mtPIIHhd95c/m/mGvQuh_OAQAJ
    Declaration of package constants in form "CONSTANT <name> charactser set ... collate ... = <value>"
        https://groups.google.com/g/firebird-devel/c/5ehuR18Wemk
    Delaration of package constant in form "CONSTANT foo int = NULL" crashes FB:
        https://groups.google.com/g/firebird-devel/c/kze2LTWaeco/m/s1sLoIA2AQAJ

    [02.06.2026] pzotov
    All constants in the package BODY must be declared *before* units.
    See: https://groups.google.com/g/firebird-devel/c/kCFeM5-tmSQ/m/LpGJF0V-AwAJ

    Checked on 6.0.0.1978-12b2158.
"""
import locale
import re
from difflib import unified_diff
from pathlib import Path

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError

db = db_factory()
act = python_act('db')
tmp_fbk = temp_file('tmp_pkg_const_br.fbk')
tmp_user = user_factory('db', name = 'john', password = '123')
tmp_role = role_factory('db', name = 'const_reader')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_fbk: Path, tmp_user: User, tmp_role: Role, capsys):

    # Generate packages (literal constants; arith expressons; built-in functions):

    with act.db.connect(charset = 'utf8') as con:
        cur = con.cursor()

        # 1. Check ability to declare package constants of every known Firebird data types:
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
           ,'t_utf8_regular'    : ('varchar(255) character set utf8',  ("'შობას გილოცავთ'",) )         # georgian
           ,'t_utf8_ci_ai'      : ('varchar(255) character set utf8 collate unicode_ci_ai',  ("'Շնորհավոր Սուրբ Ծնունդ'",) ) # armenian
           ,'t_iso8859_1_da_da' : ('varchar(255) character set iso8859_1 collate da_da',  ("q'#Børn får søde gærøl#'",)  )
           ,'t_iso8859_1_de_de' : ('varchar(255) character set iso8859_1 collate de_de',  ("q'#Müßiggänger müssen süße Äpfel grüßen#'",)  )
           ,'t_iso8859_1_fr_fr' : ('varchar(255) character set iso8859_1 collate fr_fr',  ("q'#L'été, là-bas, ç'a été délicieux#'",)  )
           # from test_ee3e78b8.py:
           ,'t_blob_text_pi'    : ('blob sub_type 1', ("_utf8 q'#le rapport constant de la circonférence d'un cercle à son diamètre#' collate unicode_ci_ai",) )
           ,'t_blob_text_c'     : ('blob sub_type 1 character set utf8 collate unicode_ci_ai', ("q'#la constante c'est une constante physique fondamentale et sert à définir le mètre comme étant la distance parcourue par la lumière dans le vide#'",) )
        }

        pg_head_lines = ['create or alter package pg_const_literals as', 'begin']
        pg_body_lines = ['recreate package body pg_const_literals as', 'begin' ]

        # ACHTUNG: all constants in the package BODY must be declared *before* units.
        # https://groups.google.com/g/firebird-devel/c/kCFeM5-tmSQ/m/LpGJF0V-AwAJ
        for k, v in types_map.items():
            decl_type = v[0]
            check_lst = v[1]
            for idx,p in enumerate(check_lst):
                pg_head_lines.extend([f'constant {k}_head_{idx} {decl_type} = {p};'])
                pg_body_lines.extend([f'constant {k}_body_{idx} {decl_type} = {p};'])

        for k, v in types_map.items():
            decl_type = v[0]
            check_lst = v[1]
            for idx,p in enumerate(check_lst):
                ddl_pkg_head = f"""
                        procedure {k}_sp_{idx} returns(out_head_const {decl_type}, out_body_const {decl_type});
                        function {k}_fn_{idx} returns {decl_type};
                """
                pg_head_lines.extend(ddl_pkg_head.splitlines())

                ddl_pkg_body = f"""
                        procedure {k}_sp_{idx} returns(out_head_const {decl_type}, out_body_const {decl_type}) as
                        begin
                            out_head_const = {k}_head_{idx};
                            out_body_const = {k}_body_{idx};
                            suspend;
                        end

                        function {k}_fn_{idx} returns {decl_type} as
                        begin
                            return coalesce({k}_body_{idx}, {k}_head_{idx});
                        end
                """
                pg_body_lines.extend(ddl_pkg_body.splitlines())

        pg_head_lines.extend(['end'])
        pg_body_lines.extend(['end'])

        con.execute_immediate('\n'.join(pg_head_lines))
        con.execute_immediate('\n'.join(pg_body_lines))
        con.execute_immediate(f'grant usage on package pg_const_literals to role {tmp_role.name}')
        #con.commit()

        # --==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++

        # Assertion from doc:
        #     The following expressions are valid only if all operands are constants:
        #     * Arithmetic operations unary plus/minus
        #     * Bool As Value // already checked, see above.
        #     *  ... 89+ funcs ...

        # Check ability to define constant as arithmetic expression:
        eval_lst = (
            '-  + 025'
            , '- - - -003'
            , '-41- (- (12)  +27)'                                                                              #        -56
            , '-(-((((21))))-((176)))-(-(-(113)-((-(-(219))))))'                                                #       -135
            , '(((((7+8)/(3+2)+5)/9)+(29+3)/2+(7+6)*4)+29/(45+3))'                                              #         68
            , '10450090/(2+19040000/(2+1954321/(2+1748159/(2+167349/(2+16184/(2+1337/(2+137/(2+17/(2+1)))))))))'#        412 ?
            , '-1396417113/(-5-(-9)/(-233333333/(-111)))/((-37)-(-19)*(-33)-(-29))'                             #    -439816
            , '8*-9/41'                                                                                         #    0 or -1 ?
            , '8*9/-41'                                                                                         #        -1
            , '347/-19*4/-3'                                                                                    #     13 or 24 ?
            , '347/19*-6/-2'                                                                                    #         54
            , '347/-17*-4/-3'                                                                                   #    -20 or -26 ?
            , '347/17*-6*-5/-2'                                                                                 #  -240 or -300 ?
            , '7951*-229*+-7'                                                                                   #  12745453
            , '4233199/-41*7/-(-41)'                                                                            #  -604742 or -29632393/1681 = 17627 ?
            , '757863/-319*57/- -23'                                                                            #       -959
            , '2291737/-(-28)*3'                                                                                #      27282
            , '973679137/-(719)/-19'                                                                            #   26315652
            , '65535/-+-55/3'                                                                                   #       3640
            , '((55+66) * 13 +47)/((33+44)+9)/2*(500/2/3/(4+9))'                                                #         54
            , '(9-(8-(7-(6-5))))-(-(1-(2-3)*9)/2-((5-2)*3+7)*4)'                                                #         76
            , '((5+(3/(-2)))+(4*(-3)))'                                                                         #         -8
            , '3+1/(7+1/(5*3+1/(1+1/((4*(9*8+1))))))'                                                           #          3
            , '((-7)-(-(-(-(211)+27)-(-9))) )/(-3)'                                                             #        -62
            , '(-(-49)-(-((-(-(-(-(-2)-37)-(-7-(-(3)))))))))/(-2)'                                              #        -44
            , '((-(-(797739/-(32-55))-7)/2))/(-(-1137)/(-32/-9))'                                               #         45
            , '((-9)-(-((-(-(-(-(2)+19)-(-2)))))))/(-2)'                                                        #         12
            , '(((-9))-(-((-(-(-(((-(2)+17)))-(-2)))))))/(-2)'                                                  #         11
            , '- -((- - -(-(- -(((- - -((-(1197-19/(-(-(-13)-(-3)))+(-61-(-24))))))))))))'                      #       1161
            , '(-(-((-39191-(-9))/(- -4))*(-19-(-11))*((-6)-8)*(- -6- -7)/2))'                                  #   -7130760
            , '213067*(((-3))-(-((((-((-(-(((-(3)+16)))-(-7))))))))))/(-2)'                                     #     958801 

              # 970656192
            , '2147483647/( (135-(-273/(-11)))/7*(213-(-(-(-852/117)/(-92))))/7*(21-19/7+37/9)*(37-48/6-29/3-37/7-27/9)*(14-(-3-(-2-(-3-(-2))))) * (91-779/(191+49-(-9))-(-(-(-(-(-11-(-(-(-(-(-10))))))))))) )*(1000008000-999999937)*(2000000030-1999999916)*(-11-(-3)-(-9)-(-7-(-4)))*((-17-(-3)-(-9)-(-12-(-4)))*(19-34/2))*(((((((((10000000+9)/7+8 )/3+29)/4+ 16)/9+17)/6+18)/3+19)/8/3-1)/7)'

              # -59631
            , '2147483647/( (733-(-134/(-83)))/7*(219-(-(-(-619/347)/(-73))))/3*(13-13/7+19/3)*(17-78/6-21/3-39/3-29/7)*(28-(-3-(-2-(-3-(-2))))) * (16-777/(91+41-(-9))-(-(-(-(-(-11-(-(-(-(-(-10))))))))))))*(1000000000-999999997)*(2000000000-1999999996)*(-10-(-3)-(-9)-(-7-(-4)))*((-77-(-3)-(-9)-(-12-(-4)))*(19-31/2))*(((((((((10800900+9)/2+8 )/13+15999774)/141+ 16)/5+17)/6+198)/7+19)/3/5-1)/7)*(((-4))-(-((((-((-(-(((-(2)+16)))-(-2))))))))))/(-2)*(-3-(-9-(-8-(-7-(-6-(-5))))))/(-9-(-2-(-3-(-4))))/(-739-(-511))-(-1947777/(-31))'
        ) 

        pg_head_lines = ['create or alter package pg_const_eval_arith_expr as', 'begin']
        pg_body_lines = ['recreate package body pg_const_eval_arith_expr as', 'begin' ]

        for idx, expr in enumerate(eval_lst):
            pg_head_lines.extend([f'constant k_head_{idx} int128 = {expr};'])
            pg_body_lines.extend([f'constant k_body_{idx} int128 = {expr};'])

        pg_head_lines.extend(['end'])
        pg_body_lines.extend(['end'])

        con.execute_immediate('\n'.join(pg_head_lines))
        con.execute_immediate('\n'.join(pg_body_lines))
        con.execute_immediate(f'grant usage on package pg_const_eval_arith_expr to role {tmp_role.name}')
        #con.commit()

        # --==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++--==++

        # Some of built-in functions (part of these examples see also in the test for core-4460):
        funcs_map  = {
              'abs'                   : ( 'int128', 'abs(-170141183460469231731687303715884105727)'  )
            , 'ascii_char'            : ( 'char(1)', 'ascii_char(65)' )
            , 'ascii_val'             : ( 'int', "ascii_val('W')" )
            , 'base64_decode'         : ( 'blob sub_type binary', "base64_decode('VGVzdCBiYXNlNjQ=')" )
            , 'base64_encode'         : ( 'blob sub_type text character set ascii', "base64_encode('Test base64')" )
            , 'bin_and'               : ( 'int128', 'bin_and(1,3,7) + bin_not(137) + bin_or(1,3,7) + bin_shl(1024,4) + bin_shr(1024,4) + bin_xor(137, 23)' )
            , 'case'                  : ( 'varchar(3)', "case sign(exp(1)-pi()) when 1 then 'foo' else 'bar' end" )
            , 'cast'                  : ( 'varchar(3)', "cast(123 as varchar(3))" )
            , 'char_length'           : ( 'int', "char_length('qwerty')" )
            , 'char_to_uuid'          : ( 'binary(16)', "char_to_uuid('A0bF4E45-3029-2a44-D493-4998c9b439A3')" )
            , 'coalesce'              : ( 'int', 'coalesce(null, null, null, null, 7890, null)' )
            , 'compare_decfloat'      : ( 'smallint', "compare_decfloat(2.17, 2.170)" )
            , 'crypt_hash'            : ( 'blob sub_type binary', "crypt_hash('AbcdAbcdAbcdAbcd' using sha256)" )
            , 'dateadd'               : ( 'timestamp', "dateadd(315537897599999 millisecond to timestamp '01.01.0001 00:00:00.000')" )
            , 'datediff'              : ( 'bigint', "datediff(millisecond from timestamp '01.01.0001 00:00:00.000' to timestamp '31.12.9999 23:59:59.999')" )
            , 'decode'                : ( 'char(1)', "decode( sign(pi()), -1,'-', 0, '0', 1, '+',  '?')" )
            , 'decrypt'               : ( 'blob sub_type binary', "decrypt(x'0154090759DF' using sober128 key 'AbcdAbcdAbcdAbcd' iv '01234567')" )
            , 'encrypt'               : ( 'blob sub_type binary', "encrypt('897897' using sober128 key 'AbcdAbcdAbcdAbcd' iv '01234567')" )
            , 'extract'               : ( 'smallint', "extract( weekday from timestamp '31.12.9999 23:59:59.999' )" )
            , 'first_day'             : ( 'timestamp', "first_day( of quarter from timestamp '31.12.9999 23:59:59.999')" )
            , 'hex_decode'            : ( 'blob sub_type binary', "hex_decode('48657861646563696D616C')" )
            , 'hex_encode'            : ( 'blob sub_type binary', "hex_encode('Hexadecimal')" )
            
            # from test_5d04fe75.py ; see also
            # https://groups.google.com/g/firebird-devel/c/mtPIIHhd95c/m/mGvQuh_OAQAJ
            , 'iif'                   : ( 'int', 'iif(pi() > 3, 1, 0)')

            , 'last_day'              : ( 'timestamp', "last_day( of month from timestamp '01.02.0004 00:00:00.000')" )
            , 'left'                  : ( 'varchar(3)', "left('qwerty',3)" )
            , 'lower'                 : ( 'varchar(3)', "lower('ZXC')" )
            , 'lpad'                  : ( 'varchar(3)', "lpad('', 3, 'qwe')" )
            , 'ltrim'                 : ( 'varchar(3)', "ltrim('    qwe')" )
            , 'make_dbkey'            : ( 'binary(8)', "make_dbkey('RDB$RELATIONS', 0)" )
            , 'maxvalue'              : ( 'int128', 'maxvalue(-170141183460469231731687303715884105728, 170141183460469231731687303715884105727)' ) # 2do: add nulls later
            , 'minvalue'              : ( 'int128', 'minvalue(-170141183460469231731687303715884105728, 170141183460469231731687303715884105727)' ) # 2do: add nulls later
            , 'mod'                   : ( 'int', 'mod(19,4)' )
            , 'normalize_decfloat'    : ( 'decfloat', "normalize_decfloat(123456.78)" )
            
            # from test_5d04fe75.py ; see also
            # https://groups.google.com/g/firebird-devel/c/mtPIIHhd95c/m/mGvQuh_OAQAJ 
            , 'nullif'                : ( 'int', 'nullif( sign(pi()), 1 )')

            , 'octet_length'          : ( 'int', "octet_length('qwerty')" )
            , 'overlay'               : ( 'blob sub_type text', "overlay ('goodbye' placing 'hello' from 2)" )
            , 'position'              : ( 'int', "position('qwe' in 'zxcasdqweiop')" )
            , 'power'                 : ( 'double precision', 'power(pi(), exp(1))' )
            , 'quantize'              : ( 'decfloat', "quantize(0.1, 9.9)" )
            , 'replace'               : ( 'varchar(10)', "replace('qweqweiop', 'qwe', 'XXX')" )
            , 'reverse'               : ( 'varchar(10)', "reverse('qweqweiop')" )
            , 'right'                 : ( 'varchar(3)', "right('qwerty',3)" )
            , 'round'                 : ( 'numeric(3,2)', 'round(pi(),2)' )
            , 'rpad'                  : ( 'varchar(3)', "rpad('', 3, 'qwe')" )
            # --------------------------------------------------------------------------
            # *** DEFERRED ***
            # 336068934 : The constant ... must be initialized by a constant expression:
            #, 'rsa_decrypt'           : ( 'blob sub_type binary', "rsa_decrypt('Some message' key rsa_private(256))" )
            #, 'rsa_encrypt'           : ( 'blob sub_type binary', "rsa_encrypt('Some message' key rsa_public(rsa_private(256))" )
            #, 'rsa_sign_hash'         : ( 'blob sub_type binary', "rsa_sign_hash(crypt_hash('Test message' using sha256) key rdb$get_context('USER_SESSION', 'private_key'))" )
            #, 'rsa_verify_hash'       : ( 'boolean', "rsa_verify_hash(crypt_hash('Test message' using sha256) signature rdb$get_context('USER_SESSION', 'msg') key rdb$get_context('USER_SESSION', 'public_key'))" )
            # --------------------------------------------------------------------------
            , 'rtrim'                 : ( 'varchar(32765)', "rtrim('    qwe')" )
            , 'sign'                  : ( 'smallint', 'sign(1)' )
            , 'substring'             : ( 'varchar(32765)', "substring('qwertyuio' from 2 for 5)" )
            , 'totalorder'            : ( 'smallint', "totalorder(-0, 0)" )
            , 'trim'                  :  ("varchar(32765)", "trim('    qwerty   ')" )
            , 'trunc'                 : ( 'smallint', 'trunc(exp(1))' )
            , 'unicode_char'          : ( 'char character set utf8', "unicode_char(0x227b)" )
            , 'unicode_val'           : ( 'int', "unicode_val(unicode_char(0x227b))" )
            , 'upper'                 : ( 'varchar(3)', "upper('qwe')" )
            , 'uuid_to_char'          : ( 'char(36)', "uuid_to_char(char_to_uuid('A0bF4E45-3029-2a44-D493-4998c9b439A3'))" )
        }

        pg_head_lines = ['create or alter package pg_const_builtin_func as', 'begin']
        pg_body_lines = ['recreate package body pg_const_builtin_func as', 'begin' ]
        for k, v in funcs_map.items():
            decl_type = v[0]
            check_lst = v[1:]
            for idx,p in enumerate(check_lst):
                pg_head_lines.extend([f'constant {k}_head_{idx} {decl_type} = {p};'])
                pg_body_lines.extend([f'constant {k}_body_{idx} {decl_type} = {p};'])

        pg_head_lines.extend(['end'])
        pg_body_lines.extend(['end'])

        con.execute_immediate('\n'.join(pg_head_lines))
        con.execute_immediate('\n'.join(pg_body_lines))
        con.execute_immediate(f'grant usage on package pg_const_builtin_func to role {tmp_role.name}')
        con.execute_immediate(f'grant {tmp_role.name} to {tmp_user.name}')
        con.commit()

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == ''
    act.reset()

    ####################################################################
    # Check that non-privileged user (who has been granted to use package constants)
    # really *has* access to constants of some package 'pg_const_literals':

    with act.db.connect(user = tmp_user.name, password = tmp_user.password, role = tmp_role.name, charset = 'utf8') as con_usr:
        cur_user = con_usr.cursor()
        constants_lst = []
        for k, v in types_map.items():
            decl_type = v[0]
            check_lst = v[1]
            for idx,p in enumerate(check_lst):
                #pg_head_lines.extend([f'constant {k}_head_{idx} {decl_type} = {p};'])
                constants_lst.append( f'pg_const_literals.{k}_head_{idx}' )
        constants_sql = 'select ' + ','.join(constants_lst) + ' from rdb$database'
        try:
            cur_user.execute(constants_sql)
            for r in cur_user:
                pass
        except DatabaseError as e:
            print( e.__str__() )
            print(e.gds_codes)

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == ''
    act.reset()

    ####################################################################
    # Obtain original metadata, run backup and restore (STDERR must be empty):
    
    init_meta = act.extract_meta(charset = 'utf8', io_enc = 'utf8')
    for bkp_cmd in ('-b', '-rep'):
        if bkp_cmd == '-b':
            act.gbak(switches=[bkp_cmd, '-v', act.db.dsn, str(tmp_fbk)], io_enc = locale.getpreferredencoding())
        else:
            act.gbak(switches=[bkp_cmd, '-v', str(tmp_fbk), act.db.dsn ], io_enc = locale.getpreferredencoding())
        assert act.clean_stderr == '', f'At least one error found for {bkp_cmd=}'
        assert act.return_code == 0, f'Return code for {bkp_cmd=} is {act.return_code}.'
        act.reset()

    ####################################################################
    # Obtain metadata after restore and compare with original one. No difference must exists:

    curr_meta = act.extract_meta(charset = 'utf8', io_enc = 'utf8')

    meta_diff = unified_diff(init_meta, curr_meta)
    if any(meta_diff):
        print('UNEXPECTED. INITIAL METADATA NOT EQUALS TO CURRENT ONE:')
        for line in meta_diff:
            if line.startswith('+'):
                print(line)
    
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == '', 'Metadata script differs for databases before and after b/r.'
    act.reset()
