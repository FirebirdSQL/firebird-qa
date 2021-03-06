#coding:utf-8
#
# id:           functional.tabloid.eqc_136030
# title:        Check ability for preparing and then run query with parameters. Query should use ORDER-BY clause.
# decription:   
#                   02.02.2019: removed from DB metadata calls to UDFs - they are not used in this test but can not be used in FB 4.0 by default.
#                   Removed triggers because they have no deal here.
#                   Checked on:
#                       3.0.5.33097: OK, 2.782s.
#                       4.0.0.1421: OK, 3.642s.
#                
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import zipfile
#  
#  os.environ["ISC_USER"] = 'SYSDBA'
#  os.environ["ISC_PASSWORD"] = 'masterkey'
#  
#  db_conn.close()
#  zf = zipfile.ZipFile( os.path.join(context['files_location'],'eqc136030.zip') )
#  zf.extractall( context['temp_directory'] )
#  zf.close()
#  
#  fbk = os.path.join(context['temp_directory'],'eqc136030.fbk')
#  
#  runProgram('gbak',['-rep',fbk, dsn])
#  
#  script="""
#      set list on;
#      set sqlda_display on;
#      set planonly;
#      
#      select
#          a.csoc, a.nreserc ,  a.coddoc , a.codgio ,
#          a.macchina, a.rec_upd, a.utente_upd, 
#          cast(a.fblc as integer) fblc, 
#          cast(a.fdel as integer) fdel,
#          b.tipdoc, b.desdoc, b.fblc , c.tipgio, c.desgio , c.fblc
#      from docgio a
#      left join doctip (a.csoc, a.nreserc) b on ( a.coddoc = b.coddoc )
#      left join giotip (a.csoc, a.nreserc) c on (a.codgio = c.codgio)
#      where
#          a.csoc = ?
#          and a.nreserc = ?
#      order by a.codgio, a.coddoc;
#      
#      set planonly;
#      set plan off;
#      set sqlda_display off;
#      
#      select
#          a.csoc, a.nreserc ,  a.coddoc , a.codgio ,
#          a.macchina, a.rec_upd, a.utente_upd, 
#          cast(a.fblc as integer) fblc, 
#          cast(a.fdel as integer) fdel,
#          b.tipdoc, b.desdoc, b.fblc , c.tipgio, c.desgio , c.fblc
#      from docgio a
#      left join doctip (a.csoc, a.nreserc) b on ( a.coddoc = b.coddoc )
#      left join giotip (a.csoc, a.nreserc) c on (a.codgio = c.codgio)
#      where
#          a.csoc = 'DEM1' -- :csoc
#          and a.nreserc = '' -- :nreserc
#      order by a.codgio, a.coddoc;
#  """
#  runProgram('isql',[dsn,'-q'],script)
#  
#  ###############################
#  # Cleanup.
#  os.remove(fbk)
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INPUT message field count: 2
    01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 4 charset: 0 NONE
      :  name:   alias: 
      : table:   owner: 
    02: sqltype: 448 VARYING scale: 0 subtype: 0 len: 2 charset: 0 NONE
      :  name:   alias: 
      : table:   owner: 

    PLAN JOIN (JOIN (A ORDER DOCGIO_PK, B NATURAL), C NATURAL)

    OUTPUT message field count: 15
    01: sqltype: 448 VARYING scale: 0 subtype: 0 len: 4 charset: 0 NONE
      :  name: CSOC  alias: CSOC
      : table: DOCGIO  owner: SYSDBA
    02: sqltype: 448 VARYING scale: 0 subtype: 0 len: 2 charset: 0 NONE
      :  name: NRESERC  alias: NRESERC
      : table: DOCGIO  owner: SYSDBA
    03: sqltype: 448 VARYING scale: 0 subtype: 0 len: 3 charset: 0 NONE
      :  name: CODDOC  alias: CODDOC
      : table: DOCGIO  owner: SYSDBA
    04: sqltype: 448 VARYING scale: 0 subtype: 0 len: 3 charset: 0 NONE
      :  name: CODGIO  alias: CODGIO
      : table: DOCGIO  owner: SYSDBA
    05: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 30 charset: 0 NONE
      :  name: MACCHINA  alias: MACCHINA
      : table: DOCGIO  owner: SYSDBA
    06: sqltype: 510 TIMESTAMP scale: 0 subtype: 0 len: 8
      :  name: REC_UPD  alias: REC_UPD
      : table: DOCGIO  owner: SYSDBA
    07: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
      :  name: UTENTE_UPD  alias: UTENTE_UPD
      : table: DOCGIO  owner: SYSDBA
    08: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
      :  name: CAST  alias: FBLC
      : table:   owner: 
    09: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
      :  name: CAST  alias: FDEL
      : table:   owner: 
    10: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 3 charset: 0 NONE
      :  name: TIPDOC  alias: TIPDOC
      : table: DOCTIP  owner: SYSDBA
    11: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 60 charset: 0 NONE
      :  name: DESDOC  alias: DESDOC
      : table: DOCTIP  owner: SYSDBA
    12: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 1 charset: 0 NONE
      :  name: FBLC  alias: FBLC
      : table: DOCTIP  owner: SYSDBA
    13: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 3 charset: 0 NONE
      :  name: TIPGIO  alias: TIPGIO
      : table: GIOTIP  owner: SYSDBA
    14: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 60 charset: 0 NONE
      :  name: DESGIO  alias: DESGIO
      : table: GIOTIP  owner: SYSDBA
    15: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 1 charset: 0 NONE
      :  name: FBLC  alias: FBLC
      : table: GIOTIP  owner: SYSDBA


    CSOC                            DEM1
    NRESERC                         
    CODDOC                          AUT
    CODGIO                          CGB
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          CGE
    CODGIO                          CGB
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          CTI
    CODGIO                          CGB
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          FAA
    CODGIO                          CGB
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          FAV
    CODGIO                          CGB
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          FTA
    CODGIO                          CGB
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          FTV
    CODGIO                          CGB
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          FAA
    CODGIO                          RAC
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          FTA
    CODGIO                          RAC
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          NCA
    CODGIO                          RAC
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          NDA
    CODGIO                          RAC
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          FAV
    CODGIO                          RFV
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          FTV
    CODGIO                          RFV
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>

    CSOC                            DEM1
    NRESERC                         
    CODDOC                          NCV
    CODGIO                          RFV
    MACCHINA                        VAIO-ADAL
    REC_UPD                         2007-06-17 22:50:41.0000
    UTENTE_UPD                      1
    FBLC                            0
    FDEL                            0
    TIPDOC                          <null>
    DESDOC                          <null>
    FBLC                            <null>
    TIPGIO                          <null>
    DESGIO                          <null>
    FBLC                            <null>
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


