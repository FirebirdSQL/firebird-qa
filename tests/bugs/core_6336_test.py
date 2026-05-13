#coding:utf-8

"""
ID:          issue-6577
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/6577
TITLE:       Regression in FB 4.x: error "Implementation of text subtype <NNNN> not located" on attempt to use some collations defined in fbintl.conf [CORE6336]
DESCRIPTION:
    Test uses list of character sets and collations defined RDB$CHARACTER_SETS and RDB$COLLATIONS.
    See also $FB_HOME/intl/fbintl.conf and http://www.destructor.de/firebird/charsets.htm
    For each charset <W> we try following:
        1) alter database set default character set <W> (e.g. "ALTER DATABASE SET DEFAULT CHARACTER SET BIG_5");
        2) alter this <W> set default collation <W>, i.e. collation name is identical to the name of charset, e.g.:
           ALTER CHARACTER SET BIG_5 SET DEFAULT COLLATION BIG_5
        3) create unicode collation <U> for this <W> and alter <W> so that default collation is <U>, e.g.:
           CREATE COLLATION BIG_5_UNICODE FOR BIG_5;
           ALTER CHARACTER SET BIG_5 SET DEFAULT COLLATION [PUBLIC.]BIG_5_UNICODE;
        4) for each of other (non-unicode) collations <C> alter <W> with set default collation to <C>, e.g.
           ALTER CHARACTER SET WIN1257 SET DEFAULT COLLATION WIN1257_LV
    All these statements must pass without any error/warning etc.
    If then we:
        a) do RE-CONNECT and
        b) try to recreate trivial view based on RDB$FIELDS and
        c) run COMMIT
    -- then "Implementation of text subtype <NNNN> not located" on snapshots up to 4.0.0.2108 (inclusive).
    All above mentioned actions are accumulated (see 'ddl_lst') to be stored in dediced .sql file (see 'tmp_sql').
    ::: NB ::: To reproduce problem, one need to run ISQL and perform script with SET AUTODDL OFF.
NOTES:
    [14.07.2025] pzotov
        1. One need to save test_script into appropriate .sql file and use 'isql -i <this_file>' rather than use PIPE mechanism
        2. On FB 6.x any collation that we create must then be referred in 'ALTER CHARACTER SET' with specifying prefix 'PUBLIC.' (SQL schema),
           e.g.: alter character 'set SJIS_0208 set default collation PUBLIC.SJIS_0208_UNICODE;'
           See SQL_SCHEMA_PREFIX variable (explained by Adriano, letter 03-JUL-2025 14:59).
    [13.05.2026] pzotov
        1. Re-implemented: use RDB$CHARACTER_SETS and RDB$COLLATIONS as definitive sources for all existing character sets and collations.
           Removed hard-coded names gathered from fbintl.conf. Removed view that was used to verify stored data.
           See 'cset_coll_sql' as query that serves as source of data for further DDL actions that will be run via ES.
        2. There are several character sets (TIS620; GBK; CP943C; GB18030) which already have pre-defined unicode collations.
           For these charsets one need to *skip* 'CREATE COLLATION ***_UNICODE' statement (otherwise violation of PK/UK will raise).
           See column 'has_predefined_unicode_coll' and letter from Adriano, 20.07.2020.
        3. On 6.x we have to add SCHEMA name as prefix for UNICODE collation name (if it is not pre-defined):
               ALTER CHARACTER SET <cs_name> SET DEFAULT COLLATION PUBLIC.<cs_name>_UNICODE
           In contrary, this prefix (i.e. schema name) must NOT be used when we create regular single-byte collation
           that is registered in rdb$collations. See letter from Adriano, 03-jul-2025 14:59
        4. Setting LINGER to non-zero value allows to reduce execution time (on SS) for ~1.5x on FB-4.x/5.x and for ~3x on 6.x
           Currently there is preformance problem on every FB-6x snapshots since shared metacache introduced (6.0.0.1771).
           Sent report to Alex et al, 13.05.2026 1625.
        5. Collations NONE, OCTETS, ASCII, UNICODE_FSS, UTF8 and UCS_BASIC are not checked in this test.

    Checked on 6.0.0.1771; 5.0.5.1819; 4.0.0.2109.
"""

import shutil
from pathlib import Path
import time
import pytest
from firebird.qa import *

db = db_factory()
act = python_act('db')

tmp_sql = temp_file('tmp_core_6336.sql')

#-----------------------------------------------
def remove_excessive_leading_spaces( input_txt ):
    # Removes unneeded leading spaces from multi-line text, but with preserving indentation that was originally created.
    min_indent_to_preserve = min([len(x)-len(x.lstrip()) for x in input_txt.splitlines() if x.strip()])
    return '\n'.join( [ x[ min_indent_to_preserve : ].rstrip() for x in input_txt.splitlines() if x.strip()] )
#-----------------------------------------------

@pytest.mark.version('>=4.0')
def test_1(act: Action, tmp_sql: Path, capsys):

    SQL_SCHEMA_PREFIX = '' if act.is_version('<6') else 'PUBLIC.'
    COMMIT_TX = f"commit"
    RECONNECT = f"connect '{act.db.dsn}' user {act.db.user} password '{act.db.password}'"
    test_script = f"""
        set list on;
        set bail on;
        set blob all;
        set names utf8;
        {RECONNECT};

        set autoddl off;
        set keep_tran_params on;
        ALTER DATABASE SET LINGER TO 3; -- !
        commit;
        set transaction read committed no record_version no wait;
    """
    
    with act.db.connect() as con:
        cur = con.cursor()
        cset_coll_sql = """
            select
                trim(cs.rdb$character_set_name) as cset_name
                ,n.i
                ,cs.rdb$bytes_per_character as chr_bytes
                ,decode( n.i, 1, trim(cs.rdb$character_set_name) , 2, trim(cs.rdb$character_set_name)||'_UNICODE', 3, trim(co.rdb$collation_name) ) as coll_name
                ,co.rdb$collation_attributes as col_attr -- bit_0=no_pad_space/pad; bit_1=case_sens/case_insens; bit_2=acc_sens/acc_insens
                ,trim(max(co.rdb$base_collation_name)) as coll_base
                ,max(co.has_predefined_unicode_coll) as has_predefined_unicode_coll
            from (
                select
                    co.*
                    ,coalesce((select 1 from rdb$collations cc where cc.rdb$character_set_id = co.rdb$character_set_id and cc.rdb$collation_name = trim(co.rdb$collation_name) || '_UNICODE'),0) has_predefined_unicode_coll
                from rdb$collations co
            ) co
            join rdb$character_sets cs on co.rdb$character_set_id = cs.rdb$character_set_id
            join (select row_number()over() i from rdb$types rows 3) n on
                n.i <= 2 and trim(cs.rdb$character_set_name) = trim(co.rdb$collation_name)
                or n.i=3 and NOT
                (
                    -- exclude unicode collations for 'TIS620','GBK', 'CP943C', 'GB18030' character sets
                    -- because they are pre-defined and exists in rdb$collations (Adriano, 20.07.2020)
                    trim(co.rdb$collation_name) similar to trim(cs.rdb$character_set_name)||'(_UNICODE)?'
                )
            where
                co.rdb$system_flag = 1
                and co.rdb$collation_name not in ('NONE', 'OCTETS', 'ASCII', 'UNICODE_FSS', 'UTF8', 'UCS_BASIC')
            group by 1,2,3,4,5
            order by trim(cs.rdb$character_set_name), n.i
        """
        cur.execute(cset_coll_sql)
        cur_col_indx = { c[0].upper() : i for i,c in enumerate(cur.description) } # K = field_name; V = field_index
        cur_data_lst = cur.fetchall()

        print(cur_col_indx)
        ddl_lst = []
        for cur_data_row in cur_data_lst:
            ddl_lst.append('') # for readability, remove later
            cset_name = cur_data_row[ cur_col_indx['CSET_NAME'] ]
            coll_name = cur_data_row[ cur_col_indx['COLL_NAME'] ]
            coll_base = cur_data_row[ cur_col_indx['COLL_BASE'] ]
            chr_bytes = cur_data_row[ cur_col_indx['CHR_BYTES'] ]
            has_predefined_unicode_coll = cur_data_row[ cur_col_indx['HAS_PREDEFINED_UNICODE_COLL'] ] # 'TIS620','GBK', 'CP943C', 'GB18030'

            if chr_bytes == 4 and not coll_base:
                # if chr_bytes > 1 and not coll_base:
                coll_base = 'UNICODE'

            if cset_name == coll_name:
                ddl_lst.append(f'alter database set default character set {cset_name}')
                ddl_lst.append(f'alter character set {cset_name} /* trace_me #1 */ set default collation {cset_name}')
            else:
                # create collation FR_CA_CI_AI for ISO8859_1 FROM EXTERNAL ('FR_CA');
                # create collation FR_FR_CI_AI for ISO8859_1 FROM EXTERNAL ('FR_FR');
                from_ext_clause = f" from external('{coll_base}')" if coll_base else ''
                if has_predefined_unicode_coll:
                    # Letter from Adriano, 20-jul-2020 20:55:
                    # "Not all *_UNICODE collations was added to metadata automatically.
                    # Only some that people requested.
                    # They are registered in fbintl.conf, so one could run
                    # "CREATE COLLATION SJIS_0208_UNICODE FOR SJIS0208;" for example.
                    # Registered collations are in rdb$collations.
                    # As soon you do create collation, you are registering it.
                    # Few *_UNICODE collations are pre-registered as system collations as I said.
                    # There is no command to list fbintl.conf present items."
                    #
                    ddl_lst.append(f'alter character set {cset_name} /* trace_me #2 */set default collation {coll_name}',)
                else:
                    # fr_ca_ci_ai ; if from_ext_clause or coll_name[-8:] == '_UNICODE':
                    if coll_name[-8:] == '_UNICODE':
                        ddl_lst.append(f'create collation {coll_name} /* trace_me cur_data */ for {cset_name}{from_ext_clause}' )

                    # Letter from Adriano, 03-jul-2025 14:59:
                    # SCHEMA must be added as prefix to search collation because "ALTER CHARSET" sets the search path
                    # to the object's (<coll_name>) schema (system).
                    # For ALTER, DROP, and others statements, Firebird searches for the specified object across all schemas
                    # in the search path. The reference is bound to the first matching object found.
                    #
                    if coll_name[-8:] == '_UNICODE':
                        default_schema = SQL_SCHEMA_PREFIX
                    else:
                        default_schema = ''

                    ddl_lst.append(f'alter character set {cset_name} /* trace_me #3 */ set default collation {default_schema}{coll_name}',)

            ddl_lst.append(f'{COMMIT_TX}') # 4.x, 677eabbe: Fix #5082: Exception "too few key columns found for index" raises when attempt to create table with PK and immediatelly drop this PK within the same transaction
            ddl_lst.append(f'{RECONNECT}') # this is need to reproduce problem described in the ticket
            
            ddl_lst.append("recreate view v_dummy as select f.rdb$field_name as f_name from rdb$fields f where f.rdb$field_name = upper('dm_name')")
            ddl_lst.append("COMMIT /* ! */") # this caused SQLSTATE = 42000 / unsuccessful metadata update / -V_DUMMY / -Implementation of text subtype NNNN not located.

    with open(tmp_sql, 'w', encoding = 'utf8') as f:
        f.write(remove_excessive_leading_spaces(test_script))
        for p in ddl_lst:
            f.write('\n' + p + (';' if p.strip() else '') )

    act.isql(switches = ['-q'], input_file = tmp_sql, connect_db = False, combine_output = True, io_enc = 'utf-8' )
    assert act.clean_stdout == ''
