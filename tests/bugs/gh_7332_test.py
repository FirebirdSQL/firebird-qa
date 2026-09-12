#coding:utf-8
"""
ID:          issue-7332
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7332
TITLE:       Remove/increase the record size limit
DESCRIPTION:
    Test uses pre-created databases.conf which has alias (see variable REQUIRED_ALIAS) with following parameter:
        InlineSortThreshold = 10485760.

    Database file for that alias must NOT exist in the QA_root/files/qa/ subdirectory: it will be created and dropped here.

    Test verifies ability to create a table with total length = max possible value that is less than 1M.
    This table has single ID field and several textual columns declared in utf8 charset.
    Every row in every of these colums is result of concatenation of all unicode codepoints that require 4 bytes per character
    see list here: https://design215.com/toolbox/utf8-4byte-characters.php
    (Sumerian Cuneiform, Egyptian Hieroglyphs, Musical Symbols, Mahjong+Dominoes+Playing_Cards, Emojis)
    After successful insert of several rows in  this table, we run following query:
       "select * from test a, test b order by a.id" -- and obtain its explained execution plan.
    This plan must contain 'Refetch' item, regardless that InlineSortThreshold is 10M (i.e. much greater than doubled record size).
    All above mentioned actions are performed for three protocols: local, inet and xnet (for windows).
NOTES:
    [05.10.2025] pzotov
        One need to be sure that firebird.conf does NOT contain DatabaseAccess = None.
        Value of REQUIRED_ALIAS must be EXACTLY the same as alias specified in the pre-created databases.conf
        (for LINUX this equality is case-sensitive, even when aliases are compared!)
        Content of databases.conf must be taken from $QA_ROOT/files/qa-databases.conf (one need to replace it before every test session).
        Discussed with pcisar, letters since 30-may-2022 13:48, subject:
        "new qa, core_4964_test.py: strange outcome when use... shutil.copy() // comparing to shutil.copy2()"
        Custom driver config object ('db_cfg_object') is used: we have to use DB with predefined alias instead of temporary one.
        Checked on 6.0.0.1292-c63a3ed (SS/CS)
    [15.01.2026] pzotov
        Added substitution with suppressing table name and its alias in explained plan because it no matters.
        ::: NB ::: Order of joined sources has been changed since 6.0.0.1393-f7068cd.
        See 565bfcd6, "Fix missing inversion when the bounded ORDER plan is converted into the SORT one...".
        This is not regression (explained by dimitr, letter 14.01.2026 13:05).
        Checked on 6.0.0.1393-f7068cd; 6.0.0.1389-f784b93
"""

import re
from pathlib import Path
import pytest
import time
from firebird.qa import *
from firebird.driver import driver_config, create_database, NetProtocol, DatabaseError

substitutions = [('[ \t]+', ' '), ]
REQUIRED_ALIAS = 'tmp_gh_7332_alias'
SUCCESS_MSG = 'OK.'

db = db_factory(charset = 'utf8')

substitutions = \
    [ 
       ('record length(:)?\\s+\\d+, key length(:)?\\s+\\d+', 'record length: N, key length: M')
      ,('"PUBLIC".', '')
      ,('Table .* Full Scan', 'Table Full Scan')
      ,('"', '')
    ]
act = python_act('db', substitutions = substitutions)

# ACHTUNG! Must be equal to the values specified in the databases.conf for <REQUIRED_ALIAS>:
INLINE_SORT_THRESHOLD=10485760

# Sumerian Cuneiform, Egyptian Hieroglyphs, Musical Symbols, Mahjong+Dominoes+Playing_Cards, Emojis:
UNICODE_FOUR_BYTE_CHARS = '𒀂𒀃𒀄𒀅𒀆𒀇𒀈𒀉𒀊𒀋𒀌𒀍𒀎𒀏𒀐𒀑𒀒𒀓𒀔𒀕𒀖𒀗𒀘𒀙𒀚𒀛𒀜𒀝𒀞𒀟𒀠𒀡𒀢𒀣𒀤𒀥𒀦𒀧𒀨𒀩𒀪𒀫𒀬𒀭𒀮𒀯𒀰𒀱𒀲𒀳𒀴𒀵𒀶𒀷𒀸𒀹𒀺𒀻𒀼𒀽𒀾𒀿𒁀𒁁𒁂𒁃𒁄𒁅𒁆𒁇𒁈𒁉𒁊𒁋𒁌𒁍𒁎𒁏𒁐𒁑𒁒𒁓𒁔𒁕𒁖𒁗𒁘𒁙𒁚𒁛𒁜𒁝𒁞𒁟𒁠𒁡𒁢𒁣𒁤𒁥𒁦𒁧𒁨𒁩𒁪𒁫𒁬𒁭𒁮𒁯𒁰𒁱𒁲𒁳𒁴𒁵𒁶𒁷𒁸𒁹𒁺𒁻𒁼𒁽𒁾𒁿𒂀𒂁𒂂𒂃𒂄𒂅𒂆𒂇𒂈𒂉𒂊𒂋𒂌𒂍𒂎𒂏𒂐𒂑𒂒𒂓𒂔𒂕𒂖𒂗𒂘𒂙𒂚𒂛𒂜𒂝𒂞𒂟𒂠𒂡𒂢𒂣𒂤𒂥𒂦𒂧𒂨𒂩𒂪𒂫𒂬𒂭𒂮𒂯𒂰𒂱𒂲𒂳𒂴𒂵𒂶𒂷𒂸𒂹𒂺𒂻𒂼𒂽𒂾𒂿𒃀𒃁𒃂𒃃𒃄𒃅𒃆𒃇𒃈𒃉𒃊𒃋𒃌𒃍𒃎𒃏𒃐𒃑𒃒𒃓𒃔𒃕𒃖𒃗𒃘𒃙𒃚𒃛𒃜𒃝𒃞𒃟𒃠𒃡𒃢𒃣𒃤𒃥𒃦𒃧𒃨𒃩𒃪𒃫𒃬𒃭𒃮𒃯𒃰𒃱𒃲𒃳𒃴𒃵𒃶𒃷𒃸𒃹𒃺𒃻𒃼𒃽𒃾𒃿𒄀𒄁𒄂𒄃𒄄𒄅𒄆𒄇𒄈𒄉𒄊𒄋𒄌𒄍𒄎𒄏𒄐𒄑𒄒𒄓𒄔𒄕𒄖𒄗𒄘𒄙𒄚𒄛𒄜𒄝𒄞𒄟𒄠𒄡𒄢𒄣𒄤𒄥𒄦𒄧𒄨𒄩𒄪𒄫𒄬𒄭𒄮𒄯𒄰𒄱𒄲𒄳𒄴𒄵𒄶𒄷𒄸𒄹𒄺𒄻𒄼𒄽𒄾𒄿𒅀𒅁𒅂𒅃𒅄𒅅𒅆𒅇𒅈𒅉𒅊𒅋𒅌𒅍𒅎𒅏𒅐𒅑𒅒𒅓𒅔𒅕𒅖𒅗𒅘𒅙𒅚𒅛𒅜𒅝𒅞𒅟𒅠𒅡𒅢𒅣𒅤𒅥𒅦𒅧𒅨𒅩𒅪𒅫𒅬𒅭𒅮𒅯𒅰𒅱𒅲𒅳𒅴𒅵𒅶𒅷𒅸𒅹𒅺𒅻𒅼𒅽𒅾𒅿𒆀𒆁𒆂𒆃𒆄𒆅𒆆𒆇𒆈𒆉𒆊𒆋𒆌𒆍𒆎𒆏𒆐𒆑𒆒𒆓𒆔𒆕𒆖𒆗𒆘𒆙𒆚𒆛𒆜𒆝𒆞𒆟𒆠𒆡𒆢𒆣𒆤𒆥𒆦𒆧𒆨𒆩𒆪𒆫𒆬𒆭𒆮𒆯𒆰𒆱𒆲𒆳𒆴𒆵𒆶𒆷𒆸𒆹𒆺𒆻𒆼𒆽𒆾𒆿𒇀𒇁𒇂𒇃𒇄𒇅𒇆𒇇𒇈𒇉𒇊𒇋𒇌𒇍𒇎𒇏𒇐𒇑𒇒𒇓𒇔𒇕𒇖𒇗𒇘𒇙𒇚𒇛𒇜𒇝𒇞𒇟𒇠𒇡𒇢𒇣𒇤𒇥𒇦𒇧𒇨𒇩𒇪𒇫𒇬𒇭𒇮𒇯𒇰𒇱𒇲𒇳𒇴𒇵𒇶𒇷𒇸𒇹𒇺𒇻𒇼𒇽𒇾𒇿𒈀𒈁𒈂𒈃𒈄𒈅𒈆𒈇𒈈𒈉𒈊𒈋𒈌𒈍𒈎𒈏𒈐𒈑𒈒𒈓𒈔𒈕𒈖𒈗𒈘𒈙𒈚𒈛𒈜𒈝𒈞𒈟𒈠𒈡𒈢𒈣𒈤𒈥𒈦𒈧𒈨𒈩𒈪𒈫𒈬𒈭𒈮𒈯𒈰𒈱𒈲𒈳𒈴𒈵𒈶𒈷𒈸𒈹𒈺𒈻𒈼𒈽𒈾𒈿𒉀𒉁𒉂𒉃𒉄𒉅𒉆𒉇𒉈𒉉𒉊𒉋𒉌𒉍𒉎𒉏𒉐𒉑𒉒𒉓𒉔𒉕𒉖𒉗𒉘𒉙𒉚𒉛𒉜𒉝𒉞𒉟𒉠𒉡𒉢𒉣𒉤𒉥𒉦𒉧𒉨𒉩𒉪𒉫𒉬𒉭𒉮𒉯𒉰𒉱𒉲𒉳𒉴𒉵𒉶𒉷𒉸𒉹𒉺𒉻𒉼𒉽𒉾𒉿𒊀𒊁𒊂𒊃𒊄𒊅𒊆𒊇𒊈𒊉𒊊𒊋𒊌𒊍𒊎𒊏𒊐𒊑𒊒𒊓𒊔𒊕𒊖𒊗𒊘𒊙𒊚𒊛𒊜𒊝𒊞𒊟𒊠𒊡𒊢𒊣𒊤𒊥𒊦𒊧𒊨𒊩𒊪𒊫𒊬𒊭𒊮𒊯𒊰𒊱𒊲𒊳𒊴𒊵𒊶𒊷𒊸𒊹𒊺𒊻𒊼𒊽𒊾𒊿𒋀𒋁𒋂𒋃𒋄𒋅𒋆𒋇𒋈𒋉𒋊𒋋𒋌𒋍𒋎𒋏𒋐𒋑𒋒𒋓𒋔𒋕𒋖𒋗𒋘𒋙𒋚𒋛𒋜𒋝𒋞𒋟𒋠𒋡𒋢𒋣𒋤𒋥𒋦𒋧𒋨𒋩𒋪𒋫𒋬𒋭𒋮𒋯𒋰𒋱𒋲𒋳𒋴𒋵𒋶𒋷𒋸𒋹𒋺𒋻𒋼𒋽𒋾𒋿𒌀𒌁𒌂𒌃𒌄𒌅𒌆𒌇𒌈𒌉𒌊𒌋𒌌𒌍𒌎𒌏𒌐𒌑𒌒𒌓𒌔𒌕𒌖𒌗𒌘𒌙𒌚𒌛𒌜𒌝𒌞𒌟𒌠𒌡𒌢𒌣𒌤𒌥𒌦𒌧𒌨𒌩𒌪𒌫𒌬𒌭𒌮𒌯𒌰𒌱𒌲𒌳𒌴𒌵𒌶𒌷𒌸𒌹𒌺𒌻𒌼𒌽𒌾𒌿𒍀𒍁𒍂𒍃𒍄𒍅𒍆𒍇𒍈𒍉𒍊𒍋𒍌𒍍𒍎𒍏𒍐𒍑𒍒𒍓𒍔𒍕𒍖𒍗𒍘𒍙𒍚𒍛𒍜𒍝𒍞𒍟𒍠𒍡𒍢𒍣𒍤𒍥𒍦𒍧𒍨𒍩𒍪𒍫𒍬𒍭𒍮𒍯𒍰𒍱𒍲𒍳𒍴𒍵𒍶𒍷𒍸𒍹𒍺𒍻𒍼𒍽𒍾𒍿𒎀𒎁𒎂𒎃𒎄𒎅𒎆𒎇𒎈𒎉𒎊𒎋𒎌𒎍𒎎𒎏𒎐𒎑𒎒𒎓𒎔𒎕𒎖𒎗𒎘𒎙𒎚𒎛𒎜𒎝𒎞𒎟𓀁𓀂𓀃𓀄𓀅𓀆𓀇𓀈𓀉𓀊𓀋𓀌𓀍𓀎𓀏𓀐𓀑𓀒𓀓𓀔𓀕𓀖𓀗𓀘𓀙𓀚𓀛𓀜𓀝𓀞𓀟𓀠𓀡𓀢𓀣𓀤𓀥𓀦𓀧𓀨𓀩𓀪𓀫𓀬𓀭𓀮𓀯𓀰𓀱𓀲𓀳𓀴𓀵𓀶𓀷𓀸𓀹𓀺𓀻𓀼𓀽𓀾𓀿𓁀𓁁𓁂𓁃𓁄𓁅𓁆𓁇𓁈𓁉𓁊𓁋𓁌𓁍𓁎𓁏𓁐𓁑𓁒𓁓𓁔𓁕𓁖𓁗𓁘𓁙𓁚𓁛𓁜𓁝𓁞𓁟𓁠𓁡𓁢𓁣𓁤𓁥𓁦𓁧𓁨𓁩𓁪𓁫𓁬𓁭𓁮𓁯𓁰𓁱𓁲𓁳𓁴𓁵𓁶𓁷𓁸𓁹𓁺𓁻𓁼𓁽𓁾𓁿𓂀𓂁𓂂𓂃𓂄𓂅𓂆𓂇𓂈𓂉𓂊𓂋𓂌𓂍𓂎𓂏𓂐𓂑𓂒𓂓𓂔𓂕𓂖𓂗𓂘𓂙𓂚𓂛𓂜𓂝𓂞𓂟𓂠𓂡𓂢𓂣𓂤𓂥𓂦𓂧𓂨𓂩𓂪𓂫𓂬𓂭𓂮𓂯𓂰𓂱𓂲𓂳𓂴𓂵𓂶𓂷𓂸𓂹𓂺𓂻𓂼𓂽𓂾𓂿𓃀𓃁𓃂𓃃𓃄𓃅𓃆𓃇𓃈𓃉𓃊𓃋𓃌𓃍𓃎𓃏𓃐𓃑𓃒𓃓𓃔𓃕𓃖𓃗𓃘𓃙𓃚𓃛𓃜𓃝𓃞𓃟𓃠𓃡𓃢𓃣𓃤𓃥𓃦𓃧𓃨𓃩𓃪𓃫𓃬𓃭𓃮𓃯𓃰𓃱𓃲𓃳𓃴𓃵𓃶𓃷𓃸𓃹𓃺𓃻𓃼𓃽𓃾𓃿𓄀𓄁𓄂𓄃𓄄𓄅𓄆𓄇𓄈𓄉𓄊𓄋𓄌𓄍𓄎𓄏𓄐𓄑𓄒𓄓𓄔𓄕𓄖𓄗𓄘𓄙𓄚𓄛𓄜𓄝𓄞𓄟𓄠𓄡𓄢𓄣𓄤𓄥𓄦𓄧𓄨𓄩𓄪𓄫𓄬𓄭𓄮𓄯𓄰𓄱𓄲𓄳𓄴𓄵𓄶𓄷𓄸𓄹𓄺𓄻𓄼𓄽𓄾𓄿𓅀𓅁𓅂𓅃𓅄𓅅𓅆𓅇𓅈𓅉𓅊𓅋𓅌𓅍𓅎𓅏𓅐𓅑𓅒𓅓𓅔𓅕𓅖𓅗𓅘𓅙𓅚𓅛𓅜𓅝𓅞𓅟𓅠𓅡𓅢𓅣𓅤𓅥𓅦𓅧𓅨𓅩𓅪𓅫𓅬𓅭𓅮𓅯𓅰𓅱𓅲𓅳𓅴𓅵𓅶𓅷𓅸𓅹𓅺𓅻𓅼𓅽𓅾𓅿𓆀𓆁𓆂𓆃𓆄𓆅𓆆𓆇𓆈𓆉𓆊𓆋𓆌𓆍𓆎𓆏𓆐𓆑𓆒𓆓𓆔𓆕𓆖𓆗𓆘𓆙𓆚𓆛𓆜𓆝𓆞𓆟𓆠𓆡𓆢𓆣𓆤𓆥𓆦𓆧𓆨𓆩𓆪𓆫𓆬𓆭𓆮𓆯𓆰𓆱𓆲𓆳𓆴𓆵𓆶𓆷𓆸𓆹𓆺𓆻𓆼𓆽𓆾𓆿𓇀𓇁𓇂𓇃𓇄𓇅𓇆𓇇𓇈𓇉𓇊𓇋𓇌𓇍𓇎𓇏𓇐𓇑𓇒𓇓𓇔𓇕𓇖𓇗𓇘𓇙𓇚𓇛𓇜𓇝𓇞𓇟𓇠𓇡𓇢𓇣𓇤𓇥𓇦𓇧𓇨𓇩𓇪𓇫𓇬𓇭𓇮𓇯𓇰𓇱𓇲𓇳𓇴𓇵𓇶𓇷𓇸𓇹𓇺𓇻𓇼𓇽𓇾𓇿𓈀𓈁𓈂𓈃𓈄𓈅𓈆𓈇𓈈𓈉𓈊𓈋𓈌𓈍𓈎𓈏𓈐𓈑𓈒𓈓𓈔𓈕𓈖𓈗𓈘𓈙𓈚𓈛𓈜𓈝𓈞𓈟𓈠𓈡𓈢𓈣𓈤𓈥𓈦𓈧𓈨𓈩𓈪𓈫𓈬𓈭𓈮𓈯𓈰𓈱𓈲𓈳𓈴𓈵𓈶𓈷𓈸𓈹𓈺𓈻𓈼𓈽𓈾𓈿𓉀𓉁𓉂𓉃𓉄𓉅𓉆𓉇𓉈𓉉𓉊𓉋𓉌𓉍𓉎𓉏𓉐𓉑𓉒𓉓𓉔𓉕𓉖𓉗𓉘𓉙𓉚𓉛𓉜𓉝𓉞𓉟𓉠𓉡𓉢𓉣𓉤𓉥𓉦𓉧𓉨𓉩𓉪𓉫𓉬𓉭𓉮𓉯𓉰𓉱𓉲𓉳𓉴𓉵𓉶𓉷𓉸𓉹𓉺𓉻𓉼𓉽𓉾𓉿𓊀𓊁𓊂𓊃𓊄𓊅𓊆𓊇𓊈𓊉𓊊𓊋𓊌𓊍𓊎𓊏𓊐𓊑𓊒𓊓𓊔𓊕𓊖𓊗𓊘𓊙𓊚𓊛𓊜𓊝𓊞𓊟𓊠𓊡𓊢𓊣𓊤𓊥𓊦𓊧𓊨𓊩𓊪𓊫𓊬𓊭𓊮𓊯𓊰𓊱𓊲𓊳𓊴𓊵𓊶𓊷𓊸𓊹𓊺𓊻𓊼𓊽𓊾𓊿𓋀𓋁𓋂𓋃𓋄𓋅𓋆𓋇𓋈𓋉𓋊𓋋𓋌𓋍𓋎𓋏𓋐𓋑𓋒𓋓𓋔𓋕𓋖𓋗𓋘𓋙𓋚𓋛𓋜𓋝𓋞𓋟𓋠𓋡𓋢𓋣𓋤𓋥𓋦𓋧𓋨𓋩𓋪𓋫𓋬𓋭𓋮𓋯𓋰𓋱𓋲𓋳𓋴𓋵𓋶𓋷𓋸𓋹𓋺𓋻𓋼𓋽𓋾𓋿𓌀𓌁𓌂𓌃𓌄𓌅𓌆𓌇𓌈𓌉𓌊𓌋𓌌𓌍𓌎𓌏𓌐𓌑𓌒𓌓𓌔𓌕𓌖𓌗𓌘𓌙𓌚𓌛𓌜𓌝𓌞𓌟𓌠𓌡𓌢𓌣𓌤𓌥𓌦𓌧𓌨𓌩𓌪𓌫𓌬𓌭𓌮𓌯𓌰𓌱𓌲𓌳𓌴𓌵𓌶𓌷𓌸𓌹𓌺𓌻𓌼𓌽𓌾𓌿𓍀𓍁𓍂𓍃𓍄𓍅𓍆𓍇𓍈𓍉𓍊𓍋𓍌𓍍𓍎𓍏𓍐𓍑𓍒𓍓𓍔𓍕𓍖𓍗𓍘𓍙𓍚𓍛𓍜𓍝𓍞𓍟𓍠𓍡𓍢𓍣𓍤𓍥𓍦𓍧𓍨𓍩𓍪𓍫𓍬𓍭𓍮𓍯𓍰𓍱𓍲𓍳𓍴𓍵𓍶𓍷𓍸𓍹𓍺𓍻𓍼𓍽𓍾𓍿𓎀𓎁𓎂𓎃𓎄𓎅𓎆𓎇𓎈𓎉𓎊𓎋𓎌𓎍𓎎𓎏𓎐𓎑𓎒𓎓𓎔𓎕𓎖𓎗𓎘𓎙𓎚𓎛𓎜𓎝𓎞𓎟𓎠𓎡𓎢𓎣𓎤𓎥𓎦𓎧𓎨𓎩𓎪𓎫𓎬𓎭𓎮𓎯𓎰𓎱𓎲𓎳𓎴𓎵𓎶𓎷𓎸𓎹𓎺𓎻𓎼𓎽𓎾𓎿𓏀𓏁𓏂𓏃𓏄𓏅𓏆𓏇𓏈𓏉𓏊𓏋𓏌𓏍𓏎𓏏𓏐𓏑𓏒𓏓𓏔𓏕𓏖𓏗𓏘𓏙𓏚𓏛𓏜𓏝𓏞𓏟𓏠𓏡𓏢𓏣𓏤𓏥𓏦𓏧𓏨𓏩𓏪𓏫𓏬𓏭𓏮𓏯𓏰𓏱𓏲𓏳𓏴𓏵𓏶𓏷𓏸𓏹𓏺𓏻𓏼𓏽𓏾𓏿𓐀𓐁𓐂𓐃𓐄𓐅𓐆𓐇𓐈𓐉𓐊𓐋𓐌𓐍𓐎𓐏𓐐𓐑𓐒𓐓𓐔𓐕𓐖𓐗𓐘𓐙𓐚𓐛𓐜𓐝𓐞𓐟𓐠𓐡𓐢𓐣𓐤𓐥𓐦𓐧𓐨𓐩𓐪𓐫𓐬𓐭𓐮𓐯𝄁𝄂𝄃𝄄𝄅𝄆𝄇𝄈𝄉𝄊𝄋𝄌𝄍𝄎𝄏𝄐𝄑𝄒𝄓𝄔𝄕𝄖𝄗𝄘𝄙𝄚𝄛𝄜𝄝𝄞𝄟𝄠𝄡𝄢𝄣𝄤𝄥𝄦𝄧𝄨𝄩𝄪𝄫𝄬𝄭𝄮𝄯𝄰𝄱𝄲𝄳𝄴𝄵𝄶𝄷𝄸𝄹𝄺𝄻𝄼𝄽𝄾𝄿𝅀𝅁𝅂𝅃𝅄𝅅𝅆𝅇𝅈𝅉𝅊𝅋𝅌𝅍𝅎𝅏𝅐𝅑𝅒𝅓𝅔𝅕𝅖𝅗𝅘𝅙𝅚𝅛𝅜𝅝𝅗𝅥𝅘𝅥𝅘𝅥𝅮𝅘𝅥𝅯𝅘𝅥𝅰𝅘𝅥𝅱𝅘𝅧𝅨𝅩𝅥𝅲𝅥𝅦𝅪𝅫𝅬𝅮𝅯𝅰𝅱𝅲𝅭𝅳𝅴𝅵𝅶𝅷𝅸𝅹𝅺𝅻𝅼𝅽𝅾𝅿𝆀𝆁𝆂𝆃𝆄𝆊𝆋𝆅𝆆𝆇𝆈𝆉𝆌𝆍𝆎𝆏𝆐𝆑𝆒𝆓𝆔𝆕𝆖𝆗𝆘𝆙𝆚𝆛𝆜𝆝𝆞𝆟𝆠𝆡𝆢𝆣𝆤𝆥𝆦𝆧𝆨𝆩𝆪𝆫𝆬𝆭𝆮𝆯𝆰𝆱𝆲𝆳𝆴𝆵𝆶𝆷𝆸𝆹𝆺𝆹𝅥𝆺𝅥𝆹𝅥𝅮𝆺𝅥𝅮𝆹𝅥𝅯𝆺𝅥𝅯𝇁𝇂𝇃𝇄𝇅𝇆𝇇𝇈𝇉𝇊𝇋𝇌𝇍𝇎𝇏𝇐𝇑𝇒𝇓𝇔𝇕𝇖𝇗𝇘𝇙𝇚𝇛𝇜𝇝𝇞𝇟𝇠𝇡𝇢𝇣𝇤𝇥𝇦𝇧𝇨𝇩𝇪𝇫𝇬𝇭𝇮𝇯🀁🀂🀃🀄🀅🀆🀇🀈🀉🀊🀋🀌🀍🀎🀏🀐🀑🀒🀓🀔🀕🀖🀗🀘🀙🀚🀛🀜🀝🀞🀟🀠🀡🀢🀣🀤🀥🀦🀧🀨🀩🀪🀫🀬🀭🀮🀯🀰🀱🀲🀳🀴🀵🀶🀷🀸🀹🀺🀻🀼🀽🀾🀿🁀🁁🁂🁃🁄🁅🁆🁇🁈🁉🁊🁋🁌🁍🁎🁏🁐🁑🁒🁓🁔🁕🁖🁗🁘🁙🁚🁛🁜🁝🁞🁟🁠🁡🁢🁣🁤🁥🁦🁧🁨🁩🁪🁫🁬🁭🁮🁯🁰🁱🁲🁳🁴🁵🁶🁷🁸🁹🁺🁻🁼🁽🁾🁿🂀🂁🂂🂃🂄🂅🂆🂇🂈🂉🂊🂋🂌🂍🂎🂏🂐🂑🂒🂓🂔🂕🂖🂗🂘🂙🂚🂛🂜🂝🂞🂟🂠🂡🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂬🂭🂮🂯🂰🂱🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂼🂽🂾🂿🃀🃁🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃌🃍🃎🃏🃐🃑🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃜🃝🃞🃟🃠🃡🃢🃣🃤🃥🃦🃧🃨🃩🃪🃫🃬🃭🃮🃯🌁🌂🌃🌄🌅🌆🌇🌈🌉🌊🌋🌌🌍🌎🌏🌐🌑🌒🌓🌔🌕🌖🌗🌘🌙🌚🌛🌜🌝🌞🌟🌠🌡🌢🌣🌤🌥🌦🌧🌨🌩🌪🌫🌬🌭🌮🌯🌰🌱🌲🌳🌴🌵🌶🌷🌸🌹🌺🌻🌼🌽🌾🌿🍀🍁🍂🍃🍄🍅🍆🍇🍈🍉🍊🍋🍌🍍🍎🍏🍐🍑🍒🍓🍔🍕🍖🍗🍘🍙🍚🍛🍜🍝🍞🍟🍠🍡🍢🍣🍤🍥🍦🍧🍨🍩🍪🍫🍬🍭🍮🍯🍰🍱🍲🍳🍴🍵🍶🍷🍸🍹🍺🍻🍼🍽🍾🍿🎀🎁🎂🎃🎄🎅🎆🎇🎈🎉🎊🎋🎌🎍🎎🎏🎐🎑🎒🎓🎔🎕🎖🎗🎘🎙🎚🎛🎜🎝🎞🎟🎠🎡🎢🎣🎤🎥🎦🎧🎨🎩🎪🎫🎬🎭🎮🎯🎰🎱🎲🎳🎴🎵🎶🎷🎸🎹🎺🎻🎼🎽🎾🎿🏀🏁🏂🏃🏄🏅🏆🏇🏈🏉🏊🏋🏌🏍🏎🏏🏐🏑🏒🏓🏔🏕🏖🏗🏘🏙🏚🏛🏜🏝🏞🏟🏠🏡🏢🏣🏤🏥🏦🏧🏨🏩🏪🏫🏬🏭🏮🏯🏰🏱🏲🏳🏴🏵🏶🏷🏸🏹🏺🏻🏼🏽🏾🏿🐀🐁🐂🐃🐄🐅🐆🐇🐈🐉🐊🐋🐌🐍🐎🐏🐐🐑🐒🐓🐔🐕🐖🐗🐘🐙🐚🐛🐜🐝🐞🐟🐠🐡🐢🐣🐤🐥🐦🐧🐨🐩🐪🐫🐬🐭🐮🐯🐰🐱🐲🐳🐴🐵🐶🐷🐸🐹🐺🐻🐼🐽🐾🐿👀👁👂👃👄👅👆👇👈👉👊👋👌👍👎👏👐👑👒👓👔👕👖👗👘👙👚👛👜👝👞👟👠👡👢👣👤👥👦👧👨👩👪👫👬👭👮👯👰👱👲👳👴👵👶👷👸👹👺👻👼👽👾👿💀💁💂💃💄💅💆💇💈💉💊💋💌💍💎💏💐💑💒💓💔💕💖💗💘💙💚💛💜💝💞💟💠💡💢💣💤💥💦💧💨💩💪💫💬💭💮💯💰💱💲💳💴💵💶💷💸💹💺💻💼💽💾💿📀📁📂📃📄📅📆📇📈📉📊📋📌📍📎📏📐📑📒📓📔📕📖📗📘📙📚📛📜📝📞📟📠📡📢📣📤📥📦📧📨📩📪📫📬📭📮📯📰📱📲📳📴📵📶📷📸📹📺📻📼📽📾📿🔀🔁🔂🔃🔄🔅🔆🔇🔈🔉🔊🔋🔌🔍🔎🔏🔐🔑🔒🔓🔔🔕🔖🔗🔘🔙🔚🔛🔜🔝🔞🔟🔠🔡🔢🔣🔤🔥🔦🔧🔨🔩🔪🔫🔬🔭🔮🔯🔰🔱🔲🔳🔴🔵🔶🔷🔸🔹🔺🔻🔼🔽🔾🔿🕀🕁🕂🕃🕄🕅🕆🕇🕈🕉🕊🕋🕌🕍🕎🕏🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛🕜🕝🕞🕟🕠🕡🕢🕣🕤🕥🕦🕧🕨🕩🕪🕫🕬🕭🕮🕯🕰🕱🕲🕳🕴🕵🕶🕷🕸🕹🕺🕻🕼🕽🕾🕿🖀🖁🖂🖃🖄🖅🖆🖇🖈🖉🖊🖋🖌🖍🖎🖏🖐🖑🖒🖓🖔🖕🖖🖗🖘🖙🖚🖛🖜🖝🖞🖟🖠🖡🖢🖣🖤🖥🖦🖧🖨🖩🖪🖫🖬🖭🖮🖯🖰🖱🖲🖳🖴🖵🖶🖷🖸🖹🖺🖻🖼🖽🖾🖿🗀🗁🗂🗃🗄🗅🗆🗇🗈🗉🗊🗋🗌🗍🗎🗏🗐🗑🗒🗓🗔🗕🗖🗗🗘🗙🗚🗛🗜🗝🗞🗟🗠🗡🗢🗣🗤🗥🗦🗧🗨🗩🗪🗫🗬🗭🗮🗯🗰🗱🗲🗳🗴🗵🗶🗷🗸🗹🗺🗻🗼🗽🗾🗿😀😁😂😃😄😅😆😇😈😉😊😋😌😍😎😏😐😑😒😓😔😕😖😗😘😙😚😛😜😝😞😟😠😡😢😣😤😥😦😧😨😩😪😫😬😭😮😯😰😱😲😳😴😵😶😷😸😹😺😻😼😽😾😿🙀🙁🙂🙃🙄🙅🙆🙇🙈🙉🙊🙋🙌🙍🙎🙏🙐🙑🙒🙓🙔🙕🙖🙗🙘🙙🙚🙛🙜🙝🙞🙟🙠🙡🙢🙣🙤🙥🙦🙧🙨🙩🙪🙫🙬🙭🙮🙯🙰🙱🙲🙳🙴🙵🙶🙷🙸🙹🙺🙻🙼🙽🙾🙿🚀🚁🚂🚃🚄🚅🚆🚇🚈🚉🚊🚋🚌🚍🚎🚏🚐🚑🚒🚓🚔🚕🚖🚗🚘🚙🚚🚛🚜🚝🚞🚟🚠🚡🚢🚣🚤🚥🚦🚧🚨🚩🚪🚫🚬🚭🚮🚯🚰🚱🚲🚳🚴🚵🚶🚷🚸🚹🚺🚻🚼🚽🚾🚿🛀🛁🛂🛃🛄🛅🛆🛇🛈🛉🛊🛋🛌🛍🛎🛏🛐🛑🛒🛓🛔🛕🛖🛗🛘🛙🛚🛛🛜🛝🛞🛟🛠🛡🛢🛣🛤🛥🛦🛧🛨🛩🛪🛫🛬🛭🛮🛯🛰🛱🛲🛳🛴🛵🛶🛷🛸🛹🛺🛻🛼🛽🛾🛿🜀🜁🜂🜃🜄🜅🜆🜇🜈🜉🜊🜋🜌🜍🜎🜏🜐🜑🜒🜓🜔🜕🜖🜗🜘🜙🜚🜛🜜🜝🜞🜟🜠🜡🜢🜣🜤🜥🜦🜧🜨🜩🜪🜫🜬🜭🜮🜯🜰🜱🜲🜳🜴🜵🜶🜷🜸🜹🜺🜻🜼🜽🜾🜿🝀🝁🝂🝃🝄🝅🝆🝇🝈🝉🝊🝋🝌🝍🝎🝏🝐🝑🝒🝓🝔🝕🝖🝗🝘🝙🝚🝛🝜🝝🝞🝟🝠🝡🝢🝣🝤🝥🝦🝧🝨🝩🝪🝫🝬🝭🝮🝯🝰🝱🝲🝳🝴🝵🝶🝷🝸🝹🝺🝻🝼🝽🝾🝿🞀🞁🞂🞃🞄🞅🞆🞇🞈🞉🞊🞋🞌🞍🞎🞏🞐🞑🞒🞓🞔🞕🞖🞗🞘🞙🞚🞛🞜🞝🞞🞟🞠🞡🞢🞣🞤🞥🞦🞧🞨🞩🞪🞫🞬🞭🞮🞯🞰🞱🞲🞳🞴🞵🞶🞷🞸🞹🞺🞻🞼🞽🞾🞿🟀🟁🟂🟃🟄🟅🟆🟇🟈🟉🟊🟋🟌🟍🟎🟏🟐🟑🟒🟓🟔🟕🟖🟗🟘🟙🟚🟛🟜🟝🟞🟟🟠🟡🟢🟣🟤🟥🟦🟧🟨🟩🟪🟫🟬🟭🟮🟯🟰🟱🟲🟳🟴🟵🟶🟷🟸🟹🟺🟻🟼🟽🟾🟿🠀🠁🠂🠃🠄🠅🠆🠇🠈🠉🠊🠋🠌🠍🠎🠏🠐🠑🠒🠓🠔🠕🠖🠗🠘🠙🠚🠛🠜🠝🠞🠟🠠🠡🠢🠣🠤🠥🠦🠧🠨🠩🠪🠫🠬🠭🠮🠯🠰🠱🠲🠳🠴🠵🠶🠷🠸🠹🠺🠻🠼🠽🠾🠿🡀🡁🡂🡃🡄🡅🡆🡇🡈🡉🡊🡋🡌🡍🡎🡏🡐🡑🡒🡓🡔🡕🡖🡗🡘🡙🡚🡛🡜🡝🡞🡟🡠🡡🡢🡣🡤🡥🡦🡧🡨🡩🡪🡫🡬🡭🡮🡯🡰🡱🡲🡳🡴🡵🡶🡷🡸🡹🡺🡻🡼🡽🡾🡿🢀🢁🢂🢃🢄🢅🢆🢇🢈🢉🢊🢋🢌🢍🢎🢏🢐🢑🢒🢓🢔🢕🢖🢗🢘🢙🢚🢛🢜🢝🢞🢟🢠🢡🢢🢣🢤🢥🢦🢧🢨🢩🢪🢫🢬🢭🢮🢯🢰🢱🢲🢳🢴🢵🢶🢷🢸🢹🢺🢻🢼🢽🢾🢿🣀🣁🣂🣃🣄🣅🣆🣇🣈🣉🣊🣋🣌🣍🣎🣏🣐🣑🣒🣓🣔🣕🣖🣗🣘🣙🣚🣛🣜🣝🣞🣟🣠🣡🣢🣣🣤🣥🣦🣧🣨🣩🣪🣫🣬🣭🣮🣯🣰🣱🣲🣳🣴🣵🣶🣷🣸🣹🣺🣻🣼🣽🣾🣿🤀🤁🤂🤃🤄🤅🤆🤇🤈🤉🤊🤋🤌🤍🤎🤏🤐🤑🤒🤓🤔🤕🤖🤗🤘🤙🤚🤛🤜🤝🤞🤟🤠🤡🤢🤣🤤🤥🤦🤧🤨🤩🤪🤫🤬🤭🤮🤯🤰🤱🤲🤳🤴🤵🤶🤷🤸🤹🤺🤻🤼🤽🤾🤿🥀🥁🥂🥃🥄🥅🥆🥇🥈🥉🥊🥋🥌🥍🥎🥏🥐🥑🥒🥓🥔🥕🥖🥗🥘🥙🥚🥛🥜🥝🥞🥟🥠🥡🥢🥣🥤🥥🥦🥧🥨🥩🥪🥫🥬🥭🥮🥯🥰🥱🥲🥳🥴🥵🥶🥷🥸🥹🥺🥻🥼🥽🥾🥿🦀🦁🦂🦃🦄🦅🦆🦇🦈🦉🦊🦋🦌🦍🦎🦏🦐🦑🦒🦓🦔🦕🦖🦗🦘🦙🦚🦛🦜🦝🦞🦟🦠🦡🦢🦣🦤🦥🦦🦧🦨🦩🦪🦫🦬🦭🦮🦯🦰🦱🦲🦳🦴🦵🦶🦷🦸🦹🦺🦻🦼🦽🦾🦿🧀🧁🧂🧃🧄🧅🧆🧇🧈🧉🧊🧋🧌🧍🧎🧏🧐🧑🧒🧓🧔🧕🧖🧗🧘🧙🧚🧛🧜🧝🧞🧟🧠🧡🧢🧣🧤🧥🧦🧧🧨🧩🧪🧫🧬🧭🧮🧯🧰🧱🧲🧳🧴🧵🧶🧷🧸🧹🧺🧻🧼🧽🧾🧿'

#-----------------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):
    
    # Scan line-by-line through databases.conf, find line starting with REQUIRED_ALIAS and extract name of file that
    # must be created in the $(dir_sampleDb)/qa/ folder. This name will be used further as target database (tmp_fdb).
    # NOTE: we have to SKIP lines which are commented out, i.e. if they starts with '#':
    p_required_alias_ptn =  re.compile( '^(?!#)((^|\\s+)' + REQUIRED_ALIAS + ')\\s*=\\s*\\$\\(dir_sampleDb\\)/qa/', re.IGNORECASE )
    fname_in_dbconf = None

    with open(act.home_dir/'databases.conf', 'r') as f:
        for line in f:
            if p_required_alias_ptn.search(line):
                # If databases.conf contains line like this:
                #     tmp_7332_alias = $(dir_sampleDb)/qa/tmp_qa_7332.fdb 
                # - then we extract filename: 'tmp_qa_7332.fdb' (see below):
                fname_in_dbconf = Path(line.split('=')[1].strip()).name
                break

    # if 'fname_in_dbconf' remains undefined here then propably REQUIRED_ALIAS not equals to specified in the databases.conf!
    #
    assert fname_in_dbconf
    
    # Full path + filename of database to which we will try to connect:
    #
    tmp_fdb = Path( act.vars['sample_dir'], 'qa', fname_in_dbconf )
  
    srv_cfg = """
        [local]
        host = localhost
        user = SYSDBA
        password = masterkey
    """
    srv_cfg = driver_config.register_server(name = 'test_srv_gh_7332', config = '')

    db_cfg_name = 'tmp_7332'
    db_cfg_object = driver_config.register_database(name = db_cfg_name)
    db_cfg_object.server.value = srv_cfg.name
    db_cfg_object.protocol.value = NetProtocol.INET
    db_cfg_object.database.value = str(tmp_fdb) # REQUIRED_ALIAS

    protocols_list = [ None, NetProtocol.INET, ] # None - for local/embedded connection.
    if act.platform == 'Windows':
        protocols_list.append(NetProtocol.XNET)

    for p in protocols_list:
        db_cfg_object.protocol.value = p
        CHECKED_PROTOCOL = 'INET' if p == NetProtocol.INET else 'XNET' if p == NetProtocol.XNET else 'NONE'
        tmp_fdb.unlink(missing_ok = True)
        with create_database(db_cfg_name, user = act.db.user, password = act.db.password, charset = 'utf8') as con:
            cur = con.cursor()
            cur.execute("select a.mon$remote_protocol, g.rdb$config_value, d.mon$database_name from mon$attachments a cross join mon$database d cross join rdb$config g where a.mon$attachment_id = current_connection and g.rdb$config_name = 'InlineSortThreshold'")
            #cur.execute("select g.rdb$config_value from rdb$config g where g.rdb$config_name = 'InlineSortThreshold'")
            for r in cur:
                protocol_name = 'NONE' if not r[0] else 'INET' if r[0].upper().startswith('TCP') else 'XNET' if r[0].upper() == 'XNET'.upper() else '????'
                dbfile_name = r[2]
                #print(f'{CHECKED_PROTOCOL=}, {dbfile_name=}')
    
                print(protocol_name)
                print(r[1])
                # in case of mismatch for XNET check that there is no concurrent FB instance with same value of 'IpcName' in firebird.conf!
                # If such instance is running and was launched before currently tested FB then value of InlineSortThreshold will be taken from it!
                assert int(r[1]) == INLINE_SORT_THRESHOLD, f'{protocol_name=}: values of InlineSortThreshold not equal. Config: {r[1]}, this test: {INLINE_SORT_THRESHOLD}, {dbfile_name=}'
                

            ps, rs =  None, None
            try:
                con.execute_immediate("""
                    create table test2 (
                        id int primary key using index test2_pk
                       ,"01: Ένα (Éna)"                      varchar(8191)
                       ,"02: Δύο (Dío)"                      varchar(8191)
                       ,"03: Τρία (Tría)"                    varchar(8191)
                       ,"04: Τέσσερα (Téssera)"              varchar(8191)
                       ,"05: Πέντε (Pénte)"                  varchar(8191)
                       ,"06: Έξι (Éxi)"                      varchar(8191)
                       ,"07: Επτά (Eptá)"                    varchar(8191)
                       ,"08: Οκτώ (Októ)"                    varchar(8191)
                       ,"09: Εννέα (Ennéa)"                  varchar(8191)
                       ,"10: Δέκα (Déka)"                    varchar(8191)
                       ,"11: Έντεκα (Énteka)"                varchar(8191)
                       ,"12: Δώδεκα (Dódeka)"                varchar(8191)
                       ,"13: Δεκατρία (Dekatría)"            varchar(8191)
                       ,"14: Δεκατέσσερα (Dekatéssera)"      varchar(8191)
                       ,"15: Δεκαπέντε (Dekapénte)"          varchar(8191)
                       ,"16: Δεκαέξι (Dekáexi)"              varchar(8191)
                       ,"17: Δεκαεπτά (Dekáepеtá)"           varchar(8191)
                       ,"18: Δεκαοκτώ (Dekaoктó)"            varchar(8191)
                       ,"19: Δεκαεννέα (Dekáennéa)"          varchar(8191)
                       ,"20: Είκοσι (Íkosi)"                 varchar(8191)
                       ,"21: Είκοσι ένα (Íkosi éna)"         varchar(8191)
                       ,"22: Είκοσι δύο (Íkosi dío)"         varchar(8191)
                       ,"23: Είκοσι τρία (Íkosi tría)"       varchar(8191)
                       ,"24: Είκοσι τέσσερα (Íkosi téssera)" varchar(8191)
                       ,"25: Είκοσι πέντε (Íkosi pénte)"     varchar(8191)
                       ,"26: Είκοσι έξι (Íkosi éxi)"         varchar(8191)
                       ,"27: Είκοσι επτά (Íkosi eptá)"       varchar(8191)
                       ,"28: Είκοσι οκτώ (Íkosi októ)"       varchar(8191)
                       ,"29: Είκοσι εννέα (Íkosi ennéa)"     varchar(8191)
                       ,"30: Τριάντα (Triánta)"              varchar(8191)
                       ,"31: Τριάντα ένα (Triánta éna)"      varchar(8191)
                       ,"32: Τριάντα δύο (Triánta dío)"      varchar(8191)
                       ,"33: Τριάντα τρία (Triánta tría)"    varchar(12)
                    )
                """)
                con.commit()
                con.execute_immediate( f"""
                    insert into test2 (
                         id
                        ,"01: Ένα (Éna)"
                        ,"02: Δύο (Dío)"
                        ,"03: Τρία (Tría)"
                        ,"04: Τέσσερα (Téssera)"
                        ,"05: Πέντε (Pénte)"
                        ,"06: Έξι (Éxi)"
                        ,"07: Επτά (Eptá)"
                        ,"08: Οκτώ (Októ)"
                        ,"09: Εννέα (Ennéa)"
                        ,"10: Δέκα (Déka)"
                        ,"11: Έντεκα (Énteka)"
                        ,"12: Δώδεκα (Dódeka)"
                        ,"13: Δεκατρία (Dekatría)"
                        ,"14: Δεκατέσσερα (Dekatéssera)"
                        ,"15: Δεκαπέντε (Dekapénte)"
                        ,"16: Δεκαέξι (Dekáexi)"
                        ,"17: Δεκαεπτά (Dekáepеtá)"
                        ,"18: Δεκαοκτώ (Dekaoктó)"
                        ,"19: Δεκαεννέα (Dekáennéa)"
                        ,"20: Είκοσι (Íkosi)"
                        ,"21: Είκοσι ένα (Íkosi éna)"
                        ,"22: Είκοσι δύο (Íkosi dío)"
                        ,"23: Είκοσι τρία (Íkosi tría)"
                        ,"24: Είκοσι τέσσερα (Íkosi téssera)"
                        ,"25: Είκοσι πέντε (Íkosi pénte)"
                        ,"26: Είκοσι έξι (Íkosi éxi)"
                        ,"27: Είκοσι επτά (Íkosi eptá)"
                        ,"28: Είκοσι οκτώ (Íkosi októ)"
                        ,"29: Είκοσι εννέα (Íkosi ennéa)"
                        ,"30: Τριάντα (Triánta)"
                        ,"31: Τριάντα ένα (Triánta éna)"
                        ,"32: Τριάντα δύο (Triánta dío)"
                        ,"33: Τριάντα τρία (Triánta tría)"
                    )
                    select
                        row_number()over()
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',8191, '{UNICODE_FOUR_BYTE_CHARS}')
                       ,lpad('',12, '{UNICODE_FOUR_BYTE_CHARS}')
                    from rdb$types
                    rows 5
                    """
                )
                con.commit()
                test_sql = f"""
                    select
                         a.id
                        ,a."01: Ένα (Éna)"
                        ,a."02: Δύο (Dío)"
                        ,a."03: Τρία (Tría)"
                        ,a."04: Τέσσερα (Téssera)"
                        ,a."05: Πέντε (Pénte)"
                        ,a."06: Έξι (Éxi)"
                        ,a."07: Επτά (Eptá)"
                        ,a."08: Οκτώ (Októ)"
                        ,a."09: Εννέα (Ennéa)"
                        ,a."10: Δέκα (Déka)"
                        ,a."11: Έντεκα (Énteka)"
                        ,a."12: Δώδεκα (Dódeka)"
                        ,a."13: Δεκατρία (Dekatría)"
                        ,a."14: Δεκατέσσερα (Dekatéssera)"
                        ,a."15: Δεκαπέντε (Dekapénte)"
                        ,a."16: Δεκαέξι (Dekáexi)"
                        ,a."17: Δεκαεπτά (Dekáepеtá)"
                        ,a."18: Δεκαοκτώ (Dekaoктó)"
                        ,a."19: Δεκαεννέα (Dekáennéa)"
                        ,a."20: Είκοσι (Íkosi)"
                        ,a."21: Είκοσι ένα (Íkosi éna)"
                        ,a."22: Είκοσι δύο (Íkosi dío)"
                        ,a."23: Είκοσι τρία (Íkosi tría)"
                        ,a."24: Είκοσι τέσσερα (Íkosi téssera)"
                        ,a."25: Είκοσι πέντε (Íkosi pénte)"
                        ,a."26: Είκοσι έξι (Íkosi éxi)"
                        ,a."27: Είκοσι επτά (Íkosi eptá)"
                        ,a."28: Είκοσι οκτώ (Íkosi októ)"
                        ,a."29: Είκοσι εννέα (Íkosi ennéa)"
                        ,a."30: Τριάντα (Triánta)"
                        ,a."31: Τριάντα ένα (Triánta éna)"
                        ,b.id
                        ,b."01: Ένα (Éna)"
                        ,b."02: Δύο (Dío)"
                        ,b."03: Τρία (Tría)"
                        ,b."04: Τέσσερα (Téssera)"
                        ,b."05: Πέντε (Pénte)"
                        ,b."06: Έξι (Éxi)"
                        ,b."07: Επτά (Eptá)"
                        ,b."08: Οκτώ (Októ)"
                        ,b."09: Εννέα (Ennéa)"
                        ,b."10: Δέκα (Déka)"
                        ,b."11: Έντεκα (Énteka)"
                        ,b."12: Δώδεκα (Dódeka)"
                        ,b."13: Δεκατρία (Dekatría)"
                        ,b."14: Δεκατέσσερα (Dekatéssera)"
                        ,b."15: Δεκαπέντε (Dekapénte)"
                        ,b."16: Δεκαέξι (Dekáexi)"
                        ,b."17: Δεκαεπτά (Dekáepеtá)"
                        ,b."18: Δεκαοκτώ (Dekaoктó)"
                        ,b."19: Δεκαεννέα (Dekáennéa)"
                        ,b."20: Είκοσι (Íkosi)"
                        ,b."21: Είκοσι ένα (Íkosi éna)"
                        ,b."22: Είκοσι δύο (Íkosi dío)"
                        ,b."23: Είκοσι τρία (Íkosi tría)"
                        ,b."24: Είκοσι τέσσερα (Íkosi téssera)"
                        ,b."25: Είκοσι πέντε (Íkosi pénte)"
                        ,b."26: Είκοσι έξι (Íkosi éxi)"
                        ,b."27: Είκοσι επτά (Íkosi eptá)"
                        ,b."28: Είκοσι οκτώ (Íkosi októ)"
                        ,b."29: Είκοσι εννέα (Íkosi ennéa)"
                        ,b."30: Τριάντα (Triánta)"
                        ,b."31: Τριάντα ένα (Triánta éna)"
                    from test2 a
                    cross join test2 b
                    order by 
                        a.id
                """

                ps = cur.prepare(test_sql)
                # Print explained plan with padding eash line by dots in order to see indentations:
                print( '\n'.join([replace_leading(s) for s in ps.detailed_plan.split('\n')]) )

                rs = cur.execute(ps)
                for r in cur:
                    pass

                print(SUCCESS_MSG)

            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                if rs:
                    rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                if ps:
                    ps.free()
            con.drop_database()
        # < with create_database(...)

        act.expected_stdout = f"""
            {CHECKED_PROTOCOL}
            {INLINE_SORT_THRESHOLD}
            Select Expression
            ....-> Refetch
            ........-> Sort (record length: N, key length: M)
            ............-> Nested Loop Join (inner)
            ................-> Table Full Scan
            ................-> Table Full Scan
            {SUCCESS_MSG}
        """
        act.stdout = capsys.readouterr().out
        assert act.clean_stdout == act.clean_expected_stdout

    # < for p in protocols_list
