#coding:utf-8

"""
ID:          issue-5878
ISSUE:       5878
TITLE:       Gradual slowdown compilation (create, recreate or drop) of views
DESCRIPTION:
    Test creates number of views, with indices 0, 1, ... N, so that view_0 has query only to rdb$ table(s)
    and all subsequent view have DDL which meets rule 'create view_N as select ... from vew_M' (where M = N-1).
    Number of columns in each view is <FIELDS_COUNT> (the same).
    Then test creates <PROC_COUNT> stored procedures, each is selectable and accepts <FIELDS_COUNT> input args
    with issuing single output value.
    After this, test runs ALTER statements to change DDL of proceures and views.
    Finally, test DROPs all procedures and views.
    During this work we gather statistics for every RDB$ table using con.info.get_table_access_stats().

    We evaluate production TOTAL_FOR_CHECK = VIEWS_COUNT * FIELDS_COUNT * PROC_COUNT as number to which we will
    divide number of IR occurred in RDB$DEPENDENCIES table during this test. This number can be considered as
    'total job' amount related to dependencies adjusting that must be done by all test actions.

    For 4.x snapshots before fix, it is easy to find values of VIEWS_COUNT, FIELDS_COUNT and PROC_COUNT which
    cause too big number of indexed reads in RDB$DEPENDENCIES during this test run. The ratio of these IR to
    TOTAL_FOR_CHECK is about 40...60 or can be greaters. After fix ratio became belong to scope about 3...4.

    Test verifies that ratio of IR/TOTAL_FOR_CHECK for RDB$DEPENDENCIES is less than threshold.
    It also checks that natural reads in RDB$DEPENDENCIES absent.

JIRA:        CORE-5612
NOTES:
    [19.10.2025] pzotov
        It was reported that problem was fixed 26-oct-2018 in 4.0.0.1244 ('master' at that time):
        https://github.com/FirebirdSQL/firebird/commit/2cb9e648315b9f1ec925e48618b0678a1b9959fe

        It seems that for much combinations {VIEWS_COUNT, FIELDS_COUNT, PROC_COUNT} different 'anomalities' exist
        in natural or indexed reads for misc RDB tables.
        For example, on 6.x since 6.0.0.800-b8be591 ("Feature #1113 - SQL Schemas", 10.06.2025 23:42 UTC) there are
        ~13.5M indexed reads of RDB$FIELDS for that snapshot and this problem exists up to 6.0.0.1295.
        Test verifies fix for only ONE bug that did exist for RDB$DEPENDENCIES.
        
        Thanks to dimitr for suggestion (letter 10.10.2025 09:53).
        Confirmed problem on 6.0.0.1295, fix on 6.0.0.1299.
        Checked on 6.0.0.1312; 5.0.4.1725; 4.0.7.3237
    [21.03.2026] pzotov
        Re-implemented after notes issued by dimitr (letters 19.03.26 1236; 20.03.26 0929): value of indexed reads
        will be divided on TOTAL_FOR_CHECK (see above) rather than on total number of IR for all system tables.
        This was caused by fixed regression of #8881 ('Large amount ... in RDB$USER_PRIVILEGES ...'): after this fix
        number of rows in RDB$USER_PRIVILEGES has been valuable reduced thus total count of IR also reduced.
        This, in turn, caused increasing of RATIO of indexed reads from other tables to their total, and finally
        this led to threshold exceeding for RDB$DEPENDENCIES ==> we got 'false failure'.
        Checked on 6.0.0.1835 5.0.4.1733 4.0.0.1346.
"""
import os
from pathlib import Path
import time

from firebird.driver import DatabaseError
import pytest
from firebird.qa import *

###########################
###   S E T T I N G S   ###
###########################

VIEWS_COUNT =  10
FIELDS_COUNT = 55
PROC_COUNT = 50

TOTAL_FOR_CHECK = VIEWS_COUNT * FIELDS_COUNT * PROC_COUNT

db = db_factory()
act = python_act('db')

@pytest.mark.version('>=4.0')
def test_1(act: Action, capsys):

    ###############################
    ###   T H R E S H O L D S   ###
    ###############################
    if act.is_version('<6'):
        RDB_DEPEND_IR_MAX_RATIO = 7
        RDB_DEPEND_NR_MAX_RATIO = 0
    else:
        RDB_DEPEND_IR_MAX_RATIO = 3
        RDB_DEPEND_NR_MAX_RATIO = 0

    v_entire_ddl = []

    # DDL for create procedures
    ###########################
    ddl_01_create_sp_lst = []
    v_fields_in_hdr = ','.join( [ f'f_{i}' for i in range(FIELDS_COUNT) ] )
    for i in range(PROC_COUNT):
        v_sp_out_expr = '1' if i == 0 else f'( select sum(o) from sp_{i-1}('  +  ','.join( [ f':a_{j}' for j in range(FIELDS_COUNT) ] )  + ') )'
        ddl_01_create_sp_lst.append( f'Create procedure sp_{i} ('  +  ','.join( [ f'a_{j} int' for j in range(FIELDS_COUNT) ] ) + f') returns (o int) as begin o = {v_sp_out_expr}; suspend; end\n;' )


    # DDL for create views
    ######################
    ddl_02_create_view_lst = []
    v_sp_init_params_lst = ','.join( ('d.rdb$relation_id' for j in range(FIELDS_COUNT)) )
    v_sp_next_params_lst = ','.join( (f'd.f_{j}' for j in range(FIELDS_COUNT)) )
    for i in range(VIEWS_COUNT):
        source_field_name = 'd.rdb$relation_id' if i == 0 else f'd.f_{i-1}'
        #v_fields_in_sql = '\n,'.join( [f'(select p.o from sp_{j}( ' + (v_sp_init_params_lst if i == 0 else v_sp_next_params_lst) + ') p )' for j in range(FIELDS_COUNT)] )
        v_fields_in_sql = '\n,'.join( [f'(select p.o from sp_{j % PROC_COUNT}( ' + (v_sp_init_params_lst if i == 0 else v_sp_next_params_lst) + ') p )' for j in range(FIELDS_COUNT)] )
        v_ddl_prefix = f'Create view v_test_{i}({v_fields_in_hdr}) as \nselect \n{v_fields_in_sql} \nfrom '
        ddl_02_create_view_lst.append(v_ddl_prefix + ('rdb$database as d' if i == 0 else f'v_test_{i-1} as d') + '\n;' )

    # DDL for ALTER procedures
    ##########################
    ddl_03_alter_sp_lst = []
    for i in range(PROC_COUNT):
        v_sp_out_expr = '+'.join( [ f'a_{j}' for j in range(FIELDS_COUNT) ] ) + ' + (select count(*) from ' + f'v_test_{(i-1) % VIEWS_COUNT})'
        
        # -Too many Contexts of Relation/Procedure/Views. Maximum allowed is 256:
        # v_sp_out_expr = '(select min('  +  '+'.join( [ f'f_{j}' for j in range(FIELDS_COUNT) ] )  +  f') from v_test_{(i-1) % VIEWS_COUNT})'

        ddl_03_alter_sp_lst.append( f'Alter procedure sp_{i} ('  +  ','.join( [ f'a_{j} int' for j in range(FIELDS_COUNT) ] ) + f') returns (o int) as begin o = {v_sp_out_expr}; suspend; end\n;' )

    # DDL for ALTER views
    #####################
    v_fields_in_sql = '\n,'.join( [f'(select rdb$format from rdb$relations x where x.rdb$relation_id = d.rdb$relation_id)' for i in range(FIELDS_COUNT)] )
    ddl_04_alter_view_lst = [ f'\nAlter view v_test_{i}({v_fields_in_hdr}) as\nselect\n' + v_fields_in_sql + '\nfrom rdb$pages as d\n;' for i in range(VIEWS_COUNT)]

    rdb_depend_idx_count = rdb_depend_nat_count = 0
    rdb_depend_ir_ratio = rdb_depend_nr_ratio = 999999999
    with act.db.connect() as con:

        cur=con.cursor()
        cur.execute('select rdb$relation_id, trim(rdb$relation_name) from rdb$relations where rdb$system_flag = 1')
        rdb_map = {}

        rdp_dep_stat = {} # K = mnemona; V = (NR, IR)
        rdb_dep_id = None
        for r in cur:
            rdb_map[ r[0] ] = (r[1], 0, 0) # name; NR; IR
            if r[1] == 'RDB$DEPENDENCIES':
                rdb_dep_id = r[0] 
        assert rdb_dep_id is not None

        for p in con.info.get_table_access_stats():
            t_name, nr_count, ir_count = rdb_map[ p.table_id ] 
            if p.sequential is not None:
                nr_count -= p.sequential
            if p.indexed is not None:
                ir_count -= p.indexed
            rdb_map[ p.table_id ] = (t_name, nr_count, ir_count)

        rdp_dep_stat['init'] = rdb_map.get(rdb_dep_id, ('', 0, 0))[1:]

        try:

            # creating procedures:
            #############
            for v in ddl_01_create_sp_lst:
                con.execute_immediate(v)
                con.commit()

            # creating views:
            #############
            for v in ddl_02_create_view_lst:
                con.execute_immediate(v)
                con.commit()

            # Take statistics 'snapshot' for RDB$DEPENDENCIES table, natural and indexed reads:
            stat_tuple = [ (p.sequential, p.indexed) for p in con.info.get_table_access_stats() if p.table_id == rdb_dep_id ]
            if stat_tuple:
                rdp_dep_stat['create'] = stat_tuple[0]
            else:
                rdp_dep_stat['create'] = rdp_dep_stat['init']

            #....................................................

            # altering procedures (add dependencies on views):
            #############
            for v in ddl_03_alter_sp_lst:
                con.execute_immediate(v)
                con.commit()

            # altering views:
            #############
            for i in range(VIEWS_COUNT-1,-1,-1):
                con.execute_immediate(ddl_04_alter_view_lst[i])
                con.commit()

            # altering procedures: make them empty (in order to remove dependencies on views)
            #############
            for i in range(PROC_COUNT-1,-1,-1):
                con.execute_immediate(f'alter procedure sp_{i} as begin end')
                con.commit()

            # Take statistics 'snapshot' for RDB$DEPENDENCIES table, natural and indexed reads:
            stat_tuple = [ (p.sequential, p.indexed) for p in con.info.get_table_access_stats() if p.table_id == rdb_dep_id ]
            if stat_tuple:
                rdp_dep_stat['alter'] = stat_tuple[0]
            else:
                rdp_dep_stat['alter'] = rdp_dep_stat['create']

            #....................................................

            # drop views:
            #############
            for i in range(VIEWS_COUNT-1,-1,-1):
                con.execute_immediate(f'drop view v_test_{i}')
                con.commit()

            # drop procedures:
            #############
            for i in range(PROC_COUNT-1,-1,-1):
                con.execute_immediate(f'drop procedure sp_{i}')
                con.commit()

            # Take statistics 'snapshot' for RDB$DEPENDENCIES table, natural and indexed reads:
            stat_tuple = [ (p.sequential, p.indexed) for p in con.info.get_table_access_stats() if p.table_id == rdb_dep_id ]
            if stat_tuple:
                rdp_dep_stat['drop'] = stat_tuple[0]
            else:
                rdp_dep_stat['drop'] = rdp_dep_stat['alter']

            #....................................................

            for p in con.info.get_table_access_stats():
                t_name, nr_count, ir_count = rdb_map[ p.table_id ] 
                if p.sequential is not None:
                    nr_count += p.sequential
                if p.indexed is not None:
                    ir_count += p.indexed
                rdb_map[ p.table_id ] = (t_name, nr_count, ir_count)

                if t_name == 'RDB$DEPENDENCIES':
                    rdb_depend_idx_count = ir_count
                    rdb_depend_nat_count = nr_count

            # for VIEWS_COUNT =  10, FIELDS_COUNT = 55, PROC_COUNT = 50:
            #   before fix: 4.0.0.1227: rdb_depend_ir_ratio = 58.52 ; rdb_depend_nr_ratio = 0.
            #   after fix:  4.0.0.1346: rdb_depend_ir_ratio =  3.53 ; rdb_depend_nr_ratio = 0.
            #               5.0.4.1733: rdb_depend_ir_ratio =  3.53 ; rdb_depend_nr_ratio = 0.
            #               6.0.0.1465: rdb_depend_ir_ratio =  3.53 ; rdb_depend_nr_ratio = 0. // last prior shared metacache
            #               6.0.0.1771: rdb_depend_ir_ratio =  2.10 ; rdb_depend_nr_ratio = 0. // first with shared metacache
            #               6.0.0.1835: rdb_depend_ir_ratio =  1.27 ; rdb_depend_nr_ratio = 0.
            rdb_depend_ir_ratio = rdb_depend_idx_count / TOTAL_FOR_CHECK
            rdb_depend_nr_ratio = rdb_depend_nat_count / TOTAL_FOR_CHECK
                
        except DatabaseError as e:
            print( e.__str__() )
            print(e.gds_codes)


    EXPECTED_MSG = 'Indexed and natural reads for RDB$DEPENDENCIES are ACCEPTABLE.'

    if rdb_depend_ir_ratio <= RDB_DEPEND_IR_MAX_RATIO and rdb_depend_nr_ratio <= RDB_DEPEND_NR_MAX_RATIO:
        print(EXPECTED_MSG)
    else:
        print(f'At least one of ratios for indexed and/or natural reads in RDB$DEPENDENCIES vs {TOTAL_FOR_CHECK=} is greater than max allowed.')
        print(f'Thresholds: {RDB_DEPEND_IR_MAX_RATIO=}, {RDB_DEPEND_NR_MAX_RATIO=}')
        print(f'{VIEWS_COUNT=}, {FIELDS_COUNT=}, {PROC_COUNT=}, {TOTAL_FOR_CHECK=}')
        print(f'Ratios after this test run: rdb_depend_ir_ratio={rdb_depend_ir_ratio:.4f}; rdb_depend_nr_ratio={rdb_depend_nr_ratio:.4f}')

        print('Check statistics for all system tables:')
        print('Table name'.ljust(32), 'NR'.rjust(9), 'IR'.rjust(9))
        for v in sorted(rdb_map.values()):
            if v[1] or v[2]:
                print(v[0].ljust(32), f'{v[1]:9d}', f'{v[2]:9d}')

        print('Check statistics for RDB$DEPENDENCIES per each kind of DDL:')
        print('DDL'.ljust(12), 'NR'.rjust(9), 'IR'.rjust(9))
        for k,v in rdp_dep_stat.items():
            nr = v[0] if v[0] else 0
            ir = v[1] if v[1] else 0
            print(k.ljust(12), f'{nr:9d}', f'{ir:9d}')

        v_entire_ddl.extend(ddl_01_create_sp_lst)
        v_entire_ddl.extend(ddl_02_create_view_lst)
        v_entire_ddl.extend(ddl_03_alter_sp_lst)
        v_entire_ddl.extend([x for x in reversed(ddl_04_alter_view_lst)])
        v_entire_ddl.extend([f'alter procedure sp_{i} as begin end\n;' for i in range(FIELDS_COUNT-1,-1,-1)])
        v_entire_ddl.extend([f'drop view v_test_{i}\n;' for i in range(FIELDS_COUNT-1,-1,-1)])
        v_entire_ddl.extend([f'drop procedure sp_{i}\n;' for i in range(FIELDS_COUNT-1,-1,-1)])
        
        # DO NOT DELETE! MAY BE USEFUL FOR DEBUG:
        # ---------------------------------------
        #print('Check entire DDL:')
        #for p in v_entire_ddl:
        #    print(p)

    act.expected_stdout = EXPECTED_MSG
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
