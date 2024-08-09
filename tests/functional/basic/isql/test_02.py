#coding:utf-8

"""
ID:          isql-02
TITLE:       ISQL - SHOW SYSTEM TABLES
DESCRIPTION: Check for correct output of "SHOW SYSTEM;" command on empty database.
FBTEST:      functional.basic.isql.02
"""

import pytest
from firebird.qa import *

db = db_factory()

act = isql_act('db', 'show system;')

##############################################################
# version: 3.0
##############################################################

fb3x_checked_stdout = """
Tables:
       MON$ATTACHMENTS                        MON$CALL_STACK
       MON$CONTEXT_VARIABLES                  MON$DATABASE
       MON$IO_STATS                           MON$MEMORY_USAGE
       MON$RECORD_STATS                       MON$STATEMENTS
       MON$TABLE_STATS                        MON$TRANSACTIONS
       RDB$AUTH_MAPPING                       RDB$BACKUP_HISTORY
       RDB$CHARACTER_SETS                     RDB$CHECK_CONSTRAINTS
       RDB$COLLATIONS                         RDB$DATABASE
       RDB$DB_CREATORS                        RDB$DEPENDENCIES
       RDB$EXCEPTIONS                         RDB$FIELDS
       RDB$FIELD_DIMENSIONS                   RDB$FILES
       RDB$FILTERS                            RDB$FORMATS
       RDB$FUNCTIONS                          RDB$FUNCTION_ARGUMENTS
       RDB$GENERATORS                         RDB$INDEX_SEGMENTS
       RDB$INDICES                            RDB$LOG_FILES
       RDB$PACKAGES                           RDB$PAGES
       RDB$PROCEDURES                         RDB$PROCEDURE_PARAMETERS
       RDB$REF_CONSTRAINTS                    RDB$RELATIONS
       RDB$RELATION_CONSTRAINTS               RDB$RELATION_FIELDS
       RDB$ROLES                              RDB$SECURITY_CLASSES
       RDB$TRANSACTIONS                       RDB$TRIGGERS
       RDB$TRIGGER_MESSAGES                   RDB$TYPES
       RDB$USER_PRIVILEGES                    RDB$VIEW_RELATIONS
       SEC$DB_CREATORS                        SEC$GLOBAL_AUTH_MAPPING
       SEC$USERS                              SEC$USER_ATTRIBUTES

Collations:
       ASCII                                  BIG_5
       BS_BA                                  CP943C
       CP943C_UNICODE                         CS_CZ
       CYRL                                   DA_DA
       DB_CSY                                 DB_DAN865
       DB_DEU437                              DB_DEU850
       DB_ESP437                              DB_ESP850
       DB_FIN437                              DB_FRA437
       DB_FRA850                              DB_FRC850
       DB_FRC863                              DB_ITA437
       DB_ITA850                              DB_NLD437
       DB_NLD850                              DB_NOR865
       DB_PLK                                 DB_PTB850
       DB_PTG860                              DB_RUS
       DB_SLO                                 DB_SVE437
       DB_SVE850                              DB_TRK
       DB_UK437                               DB_UK850
       DB_US437                               DB_US850
       DE_DE                                  DOS437
       DOS737                                 DOS775
       DOS850                                 DOS852
       DOS857                                 DOS858
       DOS860                                 DOS861
       DOS862                                 DOS863
       DOS864                                 DOS865
       DOS866                                 DOS869
       DU_NL                                  EN_UK
       EN_US                                  ES_ES
       ES_ES_CI_AI                            EUCJ_0208
       FI_FI                                  FR_CA
       FR_CA_CI_AI                            FR_FR
       FR_FR_CI_AI                            GB18030
       GB18030_UNICODE                        GBK
       GBK_UNICODE                            GB_2312
       ISO8859_1                              ISO8859_13
       ISO8859_2                              ISO8859_3
       ISO8859_4                              ISO8859_5
       ISO8859_6                              ISO8859_7
       ISO8859_8                              ISO8859_9
       ISO_HUN                                ISO_PLK
       IS_IS                                  IT_IT
       KOI8R                                  KOI8R_RU
       KOI8U                                  KOI8U_UA
       KSC_5601                               KSC_DICTIONARY
       LT_LT                                  NEXT
       NONE                                   NO_NO
       NXT_DEU                                NXT_ESP
       NXT_FRA                                NXT_ITA
       NXT_US                                 OCTETS
       PDOX_ASCII                             PDOX_CSY
       PDOX_CYRL                              PDOX_HUN
       PDOX_INTL                              PDOX_ISL
       PDOX_NORDAN4                           PDOX_PLK
       PDOX_SLO                               PDOX_SWEDFIN
       PT_BR                                  PT_PT
       PXW_CSY                                PXW_CYRL
       PXW_GREEK                              PXW_HUN
       PXW_HUNDC                              PXW_INTL
       PXW_INTL850                            PXW_NORDAN4
       PXW_PLK                                PXW_SLOV
       PXW_SPAN                               PXW_SWEDFIN
       PXW_TURK                               SJIS_0208
       SV_SV                                  TIS620
       TIS620_UNICODE                         UCS_BASIC
       UNICODE                                UNICODE_CI
       UNICODE_CI_AI                          UNICODE_FSS
       UTF8                                   WIN1250
       WIN1251                                WIN1251_UA
       WIN1252                                WIN1253
       WIN1254                                WIN1255
       WIN1256                                WIN1257
       WIN1257_EE                             WIN1257_LT
       WIN1257_LV                             WIN1258
       WIN_CZ                                 WIN_CZ_CI_AI
       WIN_PTBR
"""

##############################################################
# version: 4.0
##############################################################

fb4x_checked_stdout = """
    Tables:
    MON$ATTACHMENTS
    MON$CALL_STACK
    MON$CONTEXT_VARIABLES
    MON$DATABASE
    MON$IO_STATS
    MON$MEMORY_USAGE
    MON$RECORD_STATS
    MON$STATEMENTS
    MON$TABLE_STATS
    MON$TRANSACTIONS
    RDB$AUTH_MAPPING
    RDB$BACKUP_HISTORY
    RDB$CHARACTER_SETS
    RDB$CHECK_CONSTRAINTS
    RDB$COLLATIONS
    RDB$CONFIG
    RDB$DATABASE
    RDB$DB_CREATORS
    RDB$DEPENDENCIES
    RDB$EXCEPTIONS
    RDB$FIELDS
    RDB$FIELD_DIMENSIONS
    RDB$FILES
    RDB$FILTERS
    RDB$FORMATS
    RDB$FUNCTIONS
    RDB$FUNCTION_ARGUMENTS
    RDB$GENERATORS
    RDB$INDEX_SEGMENTS
    RDB$INDICES
    RDB$LOG_FILES
    RDB$PACKAGES
    RDB$PAGES
    RDB$PROCEDURES
    RDB$PROCEDURE_PARAMETERS
    RDB$PUBLICATIONS
    RDB$PUBLICATION_TABLES
    RDB$REF_CONSTRAINTS
    RDB$RELATIONS
    RDB$RELATION_CONSTRAINTS
    RDB$RELATION_FIELDS
    RDB$ROLES
    RDB$SECURITY_CLASSES
    RDB$TIME_ZONES
    RDB$TRANSACTIONS
    RDB$TRIGGERS
    RDB$TRIGGER_MESSAGES
    RDB$TYPES
    RDB$USER_PRIVILEGES
    RDB$VIEW_RELATIONS
    SEC$DB_CREATORS
    SEC$GLOBAL_AUTH_MAPPING
    SEC$USERS
    SEC$USER_ATTRIBUTES

    Collations:
    ASCII
    BIG_5
    BS_BA
    CP943C
    CP943C_UNICODE
    CS_CZ
    CYRL
    DA_DA
    DB_CSY
    DB_DAN865
    DB_DEU437
    DB_DEU850
    DB_ESP437
    DB_ESP850
    DB_FIN437
    DB_FRA437
    DB_FRA850
    DB_FRC850
    DB_FRC863
    DB_ITA437
    DB_ITA850
    DB_NLD437
    DB_NLD850
    DB_NOR865
    DB_PLK
    DB_PTB850
    DB_PTG860
    DB_RUS
    DB_SLO
    DB_SVE437
    DB_SVE850
    DB_TRK
    DB_UK437
    DB_UK850
    DB_US437
    DB_US850
    DE_DE
    DOS437
    DOS737
    DOS775
    DOS850
    DOS852
    DOS857
    DOS858
    DOS860
    DOS861
    DOS862
    DOS863
    DOS864
    DOS865
    DOS866
    DOS869
    DU_NL
    EN_UK
    EN_US
    ES_ES
    ES_ES_CI_AI
    EUCJ_0208
    FI_FI
    FR_CA
    FR_CA_CI_AI
    FR_FR
    FR_FR_CI_AI
    GB18030
    GB18030_UNICODE
    GBK
    GBK_UNICODE
    GB_2312
    ISO8859_1
    ISO8859_13
    ISO8859_2
    ISO8859_3
    ISO8859_4
    ISO8859_5
    ISO8859_6
    ISO8859_7
    ISO8859_8
    ISO8859_9
    ISO_HUN
    ISO_PLK
    IS_IS
    IT_IT
    KOI8R
    KOI8R_RU
    KOI8U
    KOI8U_UA
    KSC_5601
    KSC_DICTIONARY
    LT_LT
    NEXT
    NONE
    NO_NO
    NXT_DEU
    NXT_ESP
    NXT_FRA
    NXT_ITA
    NXT_US
    OCTETS
    PDOX_ASCII
    PDOX_CSY
    PDOX_CYRL
    PDOX_HUN
    PDOX_INTL
    PDOX_ISL
    PDOX_NORDAN4
    PDOX_PLK
    PDOX_SLO
    PDOX_SWEDFIN
    PT_BR
    PT_PT
    PXW_CSY
    PXW_CYRL
    PXW_GREEK
    PXW_HUN
    PXW_HUNDC
    PXW_INTL
    PXW_INTL850
    PXW_NORDAN4
    PXW_PLK
    PXW_SLOV
    PXW_SPAN
    PXW_SWEDFIN
    PXW_TURK
    SJIS_0208
    SV_SV
    TIS620
    TIS620_UNICODE
    UCS_BASIC
    UNICODE
    UNICODE_CI
    UNICODE_CI_AI
    UNICODE_FSS
    UTF8
    WIN1250
    WIN1251
    WIN1251_UA
    WIN1252
    WIN1253
    WIN1254
    WIN1255
    WIN1256
    WIN1257
    WIN1257_EE
    WIN1257_LT
    WIN1257_LV
    WIN1258
    WIN_CZ
    WIN_CZ_CI_AI
    WIN_PTBR

    Roles:
    RDB$ADMIN
"""

##############################################################
# version: 5.0
##############################################################

fb5x_checked_stdout = """
    Tables:
    MON$ATTACHMENTS
    MON$CALL_STACK
    MON$COMPILED_STATEMENTS
    MON$CONTEXT_VARIABLES
    MON$DATABASE
    MON$IO_STATS
    MON$MEMORY_USAGE
    MON$RECORD_STATS
    MON$STATEMENTS
    MON$TABLE_STATS
    MON$TRANSACTIONS
    RDB$AUTH_MAPPING
    RDB$BACKUP_HISTORY
    RDB$CHARACTER_SETS
    RDB$CHECK_CONSTRAINTS
    RDB$COLLATIONS
    RDB$CONFIG
    RDB$DATABASE
    RDB$DB_CREATORS
    RDB$DEPENDENCIES
    RDB$EXCEPTIONS
    RDB$FIELDS
    RDB$FIELD_DIMENSIONS
    RDB$FILES
    RDB$FILTERS
    RDB$FORMATS
    RDB$FUNCTIONS
    RDB$FUNCTION_ARGUMENTS
    RDB$GENERATORS
    RDB$INDEX_SEGMENTS
    RDB$INDICES
    RDB$KEYWORDS
    RDB$LOG_FILES
    RDB$PACKAGES
    RDB$PAGES
    RDB$PROCEDURES
    RDB$PROCEDURE_PARAMETERS
    RDB$PUBLICATIONS
    RDB$PUBLICATION_TABLES
    RDB$REF_CONSTRAINTS
    RDB$RELATIONS
    RDB$RELATION_CONSTRAINTS
    RDB$RELATION_FIELDS
    RDB$ROLES
    RDB$SECURITY_CLASSES
    RDB$TIME_ZONES
    RDB$TRANSACTIONS
    RDB$TRIGGERS
    RDB$TRIGGER_MESSAGES
    RDB$TYPES
    RDB$USER_PRIVILEGES
    RDB$VIEW_RELATIONS
    SEC$DB_CREATORS
    SEC$GLOBAL_AUTH_MAPPING
    SEC$USERS
    SEC$USER_ATTRIBUTES
    Functions:
    RDB$BLOB_UTIL.IS_WRITABLE
    RDB$BLOB_UTIL.NEW_BLOB
    RDB$BLOB_UTIL.OPEN_BLOB
    RDB$BLOB_UTIL.READ_DATA
    RDB$BLOB_UTIL.SEEK
    RDB$PROFILER.START_SESSION
    RDB$TIME_ZONE_UTIL.DATABASE_VERSION
    Procedures:
    RDB$BLOB_UTIL.CANCEL_BLOB
    RDB$BLOB_UTIL.CLOSE_HANDLE
    RDB$PROFILER.CANCEL_SESSION
    RDB$PROFILER.DISCARD
    RDB$PROFILER.FINISH_SESSION
    RDB$PROFILER.FLUSH
    RDB$PROFILER.PAUSE_SESSION
    RDB$PROFILER.RESUME_SESSION
    RDB$PROFILER.SET_FLUSH_INTERVAL
    RDB$TIME_ZONE_UTIL.TRANSITIONS
    Packages:
    RDB$BLOB_UTIL
    RDB$PROFILER
    RDB$TIME_ZONE_UTIL
    Collations:
    ASCII
    BIG_5
    BS_BA
    CP943C
    CP943C_UNICODE
    CS_CZ
    CYRL
    DA_DA
    DB_CSY
    DB_DAN865
    DB_DEU437
    DB_DEU850
    DB_ESP437
    DB_ESP850
    DB_FIN437
    DB_FRA437
    DB_FRA850
    DB_FRC850
    DB_FRC863
    DB_ITA437
    DB_ITA850
    DB_NLD437
    DB_NLD850
    DB_NOR865
    DB_PLK
    DB_PTB850
    DB_PTG860
    DB_RUS
    DB_SLO
    DB_SVE437
    DB_SVE850
    DB_TRK
    DB_UK437
    DB_UK850
    DB_US437
    DB_US850
    DE_DE
    DOS437
    DOS737
    DOS775
    DOS850
    DOS852
    DOS857
    DOS858
    DOS860
    DOS861
    DOS862
    DOS863
    DOS864
    DOS865
    DOS866
    DOS869
    DU_NL
    EN_UK
    EN_US
    ES_ES
    ES_ES_CI_AI
    EUCJ_0208
    FI_FI
    FR_CA
    FR_CA_CI_AI
    FR_FR
    FR_FR_CI_AI
    GB18030
    GB18030_UNICODE
    GBK
    GBK_UNICODE
    GB_2312
    ISO8859_1
    ISO8859_13
    ISO8859_2
    ISO8859_3
    ISO8859_4
    ISO8859_5
    ISO8859_6
    ISO8859_7
    ISO8859_8
    ISO8859_9
    ISO_HUN
    ISO_PLK
    IS_IS
    IT_IT
    KOI8R
    KOI8R_RU
    KOI8U
    KOI8U_UA
    KSC_5601
    KSC_DICTIONARY
    LT_LT
    NEXT
    NONE
    NO_NO
    NXT_DEU
    NXT_ESP
    NXT_FRA
    NXT_ITA
    NXT_US
    OCTETS
    PDOX_ASCII
    PDOX_CSY
    PDOX_CYRL
    PDOX_HUN
    PDOX_INTL
    PDOX_ISL
    PDOX_NORDAN4
    PDOX_PLK
    PDOX_SLO
    PDOX_SWEDFIN
    PT_BR
    PT_PT
    PXW_CSY
    PXW_CYRL
    PXW_GREEK
    PXW_HUN
    PXW_HUNDC
    PXW_INTL
    PXW_INTL850
    PXW_NORDAN4
    PXW_PLK
    PXW_SLOV
    PXW_SPAN
    PXW_SWEDFIN
    PXW_TURK
    SJIS_0208
    SV_SV
    TIS620
    TIS620_UNICODE
    UCS_BASIC
    UNICODE
    UNICODE_CI
    UNICODE_CI_AI
    UNICODE_FSS
    UTF8
    WIN1250
    WIN1251
    WIN1251_UA
    WIN1252
    WIN1253
    WIN1254
    WIN1255
    WIN1256
    WIN1257
    WIN1257_EE
    WIN1257_LT
    WIN1257_LV
    WIN1258
    WIN_CZ
    WIN_CZ_CI_AI
    WIN_PTBR
    Roles:
    RDB$ADMIN
    Publications:
    RDB$DEFAULT
"""

fb6x_checked_stdout = """
    Tables:
    MON$ATTACHMENTS
    MON$CALL_STACK
    MON$COMPILED_STATEMENTS
    MON$CONTEXT_VARIABLES
    MON$DATABASE
    MON$IO_STATS
    MON$MEMORY_USAGE
    MON$RECORD_STATS
    MON$STATEMENTS
    MON$TABLE_STATS
    MON$TRANSACTIONS
    RDB$AUTH_MAPPING
    RDB$BACKUP_HISTORY
    RDB$CHARACTER_SETS
    RDB$CHECK_CONSTRAINTS
    RDB$COLLATIONS
    RDB$CONFIG
    RDB$DATABASE
    RDB$DB_CREATORS
    RDB$DEPENDENCIES
    RDB$EXCEPTIONS
    RDB$FIELDS
    RDB$FIELD_DIMENSIONS
    RDB$FILES
    RDB$FILTERS
    RDB$FORMATS
    RDB$FUNCTIONS
    RDB$FUNCTION_ARGUMENTS
    RDB$GENERATORS
    RDB$INDEX_SEGMENTS
    RDB$INDICES
    RDB$KEYWORDS
    RDB$LOG_FILES
    RDB$PACKAGES
    RDB$PAGES
    RDB$PROCEDURES
    RDB$PROCEDURE_PARAMETERS
    RDB$PUBLICATIONS
    RDB$PUBLICATION_TABLES
    RDB$REF_CONSTRAINTS
    RDB$RELATIONS
    RDB$RELATION_CONSTRAINTS
    RDB$RELATION_FIELDS
    RDB$ROLES
    RDB$SECURITY_CLASSES
    RDB$TIME_ZONES
    RDB$TRANSACTIONS
    RDB$TRIGGERS
    RDB$TRIGGER_MESSAGES
    RDB$TYPES
    RDB$USER_PRIVILEGES
    RDB$VIEW_RELATIONS
    SEC$DB_CREATORS
    SEC$GLOBAL_AUTH_MAPPING
    SEC$USERS
    SEC$USER_ATTRIBUTES
    Functions:
    RDB$BLOB_UTIL.IS_WRITABLE
    RDB$BLOB_UTIL.NEW_BLOB
    RDB$BLOB_UTIL.OPEN_BLOB
    RDB$BLOB_UTIL.READ_DATA
    RDB$BLOB_UTIL.SEEK
    RDB$PROFILER.START_SESSION
    RDB$TIME_ZONE_UTIL.DATABASE_VERSION
    Procedures:
    RDB$BLOB_UTIL.CANCEL_BLOB
    RDB$BLOB_UTIL.CLOSE_HANDLE
    RDB$PROFILER.CANCEL_SESSION
    RDB$PROFILER.DISCARD
    RDB$PROFILER.FINISH_SESSION
    RDB$PROFILER.FLUSH
    RDB$PROFILER.PAUSE_SESSION
    RDB$PROFILER.RESUME_SESSION
    RDB$PROFILER.SET_FLUSH_INTERVAL
    RDB$SQL.EXPLAIN
    RDB$TIME_ZONE_UTIL.TRANSITIONS
    Packages:
    RDB$BLOB_UTIL
    RDB$PROFILER
    RDB$SQL
    RDB$TIME_ZONE_UTIL
    Collations:
    ASCII
    BIG_5
    BS_BA
    CP943C
    CP943C_UNICODE
    CS_CZ
    CYRL
    DA_DA
    DB_CSY
    DB_DAN865
    DB_DEU437
    DB_DEU850
    DB_ESP437
    DB_ESP850
    DB_FIN437
    DB_FRA437
    DB_FRA850
    DB_FRC850
    DB_FRC863
    DB_ITA437
    DB_ITA850
    DB_NLD437
    DB_NLD850
    DB_NOR865
    DB_PLK
    DB_PTB850
    DB_PTG860
    DB_RUS
    DB_SLO
    DB_SVE437
    DB_SVE850
    DB_TRK
    DB_UK437
    DB_UK850
    DB_US437
    DB_US850
    DE_DE
    DOS437
    DOS737
    DOS775
    DOS850
    DOS852
    DOS857
    DOS858
    DOS860
    DOS861
    DOS862
    DOS863
    DOS864
    DOS865
    DOS866
    DOS869
    DU_NL
    EN_UK
    EN_US
    ES_ES
    ES_ES_CI_AI
    EUCJ_0208
    FI_FI
    FR_CA
    FR_CA_CI_AI
    FR_FR
    FR_FR_CI_AI
    GB18030
    GB18030_UNICODE
    GBK
    GBK_UNICODE
    GB_2312
    ISO8859_1
    ISO8859_13
    ISO8859_2
    ISO8859_3
    ISO8859_4
    ISO8859_5
    ISO8859_6
    ISO8859_7
    ISO8859_8
    ISO8859_9
    ISO_HUN
    ISO_PLK
    IS_IS
    IT_IT
    KOI8R
    KOI8R_RU
    KOI8U
    KOI8U_UA
    KSC_5601
    KSC_DICTIONARY
    LT_LT
    NEXT
    NONE
    NO_NO
    NXT_DEU
    NXT_ESP
    NXT_FRA
    NXT_ITA
    NXT_US
    OCTETS
    PDOX_ASCII
    PDOX_CSY
    PDOX_CYRL
    PDOX_HUN
    PDOX_INTL
    PDOX_ISL
    PDOX_NORDAN4
    PDOX_PLK
    PDOX_SLO
    PDOX_SWEDFIN
    PT_BR
    PT_PT
    PXW_CSY
    PXW_CYRL
    PXW_GREEK
    PXW_HUN
    PXW_HUNDC
    PXW_INTL
    PXW_INTL850
    PXW_NORDAN4
    PXW_PLK
    PXW_SLOV
    PXW_SPAN
    PXW_SWEDFIN
    PXW_TURK
    SJIS_0208
    SV_SV
    TIS620
    TIS620_UNICODE
    UCS_BASIC
    UNICODE
    UNICODE_CI
    UNICODE_CI_AI
    UNICODE_FSS
    UTF8
    WIN1250
    WIN1251
    WIN1251_UA
    WIN1252
    WIN1253
    WIN1254
    WIN1255
    WIN1256
    WIN1257
    WIN1257_EE
    WIN1257_LT
    WIN1257_LV
    WIN1258
    WIN_CZ
    WIN_CZ_CI_AI
    WIN_PTBR
    Roles:
    RDB$ADMIN
    Publications:
    RDB$DEFAULT
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = fb3x_checked_stdout if act.is_version('<4') else fb4x_checked_stdout if act.is_version('<5') else fb5x_checked_stdout if act.is_version('<6') else fb6x_checked_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
