#coding:utf-8

"""
ID:          issue-3606
ISSUE:       3606
TITLE:       Support for text BLOBs >= 32K as first argument for TRIM()
DESCRIPTION:
JIRA:        CORE-3234
FBTEST:      bugs.core_3234
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- For single-byte (ascii) charset this test was run also two blobs with length 50'000'000 (+3) bytes: result was OK.
	-- Current settings check work of TRIM() on blobs with non-ascii characters with octet_length ~ 1'000'000 bytes.
	-- Elapsed time on P-IV 3.0 GHz / RAM 2 Gb: ~7 second.

    recreate sequence g;
    commit;

    set list on;
    set term ^;

    execute block returns(
        b1_octet_len int,
        b2_octet_len int,
        trimmed_octet_len int,
        b1_char_len int,
        b2_char_len int,
        trimmed_char_len int
    ) as
        declare b1 blob sub_type 1 character set utf8 = '';
        declare b2 blob sub_type 1 character set utf8;
        declare v_step int = 8190;
        declare v_text varchar(255) character set utf8;
        declare n int = 0;
        declare k int = 500000;
    begin
        -- http://www.columbia.edu/kermit/cp1250.html
        v_text =
        ''
        || '€' --  128  08/00  200  80  EURO SYMBOL
        || '‚' --  130  08/02  202  82  LOW 9 SINGLE QUOTE
        || '„' --  132  08/04  204  84  LOW 9 DOUBLE QUOTE
        || '…' --  133  08/05  205  85  ELLIPSIS
        || '†' --  134  08/06  206  86  DAGGER
        || '‡' --  135  08/07  207  87  DOUBLE DAGGER
        || '‰' --  137  08/09  211  89  PER MIL SIGN
        || 'Š' --  138  08/10  212  8A  CAPITAL LETTER S WITH CARON
        || '‹' --  139  08/11  213  8B  LEFT SINGLE QUOTE BRACKET
        || 'Ś' --  140  08/12  214  8C  CAPITAL LETTER S WITH ACUTE ACCENT
        || 'Ť' --  141  08/13  215  8D  CAPITAL LETTER T WITH CARON
        || 'Ž' --  142  08/14  216  8E  CAPITAL LETTER Z WITH CARON
        || 'Ź' --  143  08/15  217  8F  CAPITAL LETTER Z WITH ACUTE ACCENT
        || '‘' --  145  09/01  221  91  HIGH 6 SINGLE QUOTE
        || '’' --  146  09/02  222  92  HIGH 9 SINGLE QUOTE
        || '“' --  147  09/03  223  93  HIGH 6 DOUBLE QUOTE
        || '”' --  148  09/04  224  94  HIGH 9 DOUBLE QUOTE
        || '•' --  149  09/05  225  95  LARGE CENTERED DOT
        || '–' --  150  09/06  226  96  EN DASH
        || '—' --  151  09/07  227  97  EM DASH
        || '™' --  153  09/09  231  99  TRADEMARK SIGN
        || 'š' --  154  09/10  232  9A  SMALL LETTER S WITH CARON
        || '›' --  155  09/11  233  9B  RIGHT SINGLE QUOTE BRACKET
        || 'ś' --  156  09/12  234  9C  SMALL LETTER S WITH ACUTE ACCENT
        || 'ť' --  157  09/13  235  9D  SMALL LETTER T WITH CARON
        || 'ž' --  158  09/14  236  9E  SMALL LETTER Z WITH CARON
        || 'ź' --  159  09/15  237  9F  SMALL LETTER Z WITH ACUTE ACCENT
        || ' ' --  160  10/00  240  A0  NO-BREAK SPACE
        || 'ˇ' --  161  10/01  241  A1  CARON
        || '˘' --  162  10/02  242  A2  BREVE
        || 'Ł' --  163  10/03  243  A3  CAPITAL LETTER L WITH STROKE
        || '¤' --  164  10/04  244  A4  CURRENCY SIGN
        || 'Ą' --  165  10/05  245  A5  CAPITAL LETTER A WITH OGONEK
        || '¦' --  166  10/06  246  A6  BROKEN BAR
        || '§' --  167  10/07  247  A7  PARAGRAPH SIGN
        || '¨' --  168  10/08  250  A8  DIAERESIS
        || '©' --  169  10/09  251  A9  COPYRIGHT SIGN
        || 'Ş' --  170  10/10  252  AA  CAPITAL LETTER S WITH CEDILLA
        || '«' --  171  10/11  253  AB  LEFT ANGLE QUOTATION MARK
        || '¬' --  172  10/12  254  AC  NOT SIGN
        || '­' --  173  10/13  255  AD  SOFT HYPHEN
        || '®' --  174  10/14  256  AE  REGISTERED TRADE MARK SIGN
        || 'Ż' --  175  10/15  257  AF  CAPITAL LETTER Z WITH DOT ABOVE
        || '°' --  176  11/00  260  B0  DEGREE SIGN, RING ABOVE
        || '±' --  177  11/01  261  B1  PLUS-MINUS SIGN
        || '˛' --  178  11/02  262  B2  OGONEK
        || 'ł' --  179  11/03  263  B3  SMALL LETTER L WITH STROKE
        || '´' --  180  11/04  264  B4  ACUTE ACCENT
        || 'µ' --  181  11/05  265  B5  MICRO SIGN
        || '¶' --  182  11/06  266  B6  PILCROW SIGN
        || '·' --  183  11/07  267  B7  MIDDLE DOT
        || '¸' --  184  11/08  270  B8  CEDILLA
        || 'ą' --  185  11/09  271  B9  SMALL LETTER A WITH OGONEK
        || 'ş' --  186  11/10  272  BA  SMALL LETTER S WITH CEDILLA
        || '»' --  187  11/11  273  BB  RIGHT ANGLE QUOTATION MARK
        || 'Ľ' --  188  11/12  274  BC  CAPITAL LETTER L WITH CARON
        || '˝' --  189  11/13  275  BD  DOUBLE ACUTE ACCENT
        || 'ľ' --  190  11/14  276  BE  CAPITAL LETTER I WITH CARON
        || 'ż' --  191  11/15  277  BF  SMALL LETTER Z WITH DOT ABOVE
        || 'Ŕ' --  192  12/00  300  C0  CAPITAL LETTER R WITH ACUTE ACCENT
        || 'Á' --  193  12/01  301  C1  CAPITAL LETTER A WITH ACUTE ACCENT
        || 'Â' --  194  12/02  302  C2  CAPITAL LETTER A WITH CIRCUMFLEX
        || 'Ă' --  195  12/03  303  C3  CAPITAL LETTER A WITH BREVE
        || 'Ä' --  196  12/04  304  C4  CAPITAL LETTER A WITH DIAERESIS
        || 'Ĺ' --  197  12/05  305  C5  CAPITAL LETTER L WITH ACUTE ACCENT
        || 'Ć' --  198  12/06  306  C6  CAPITAL LETTER C WITH ACUTE ACCENT
        || 'Ç' --  199  12/07  307  C7  CAPITAL LETTER C WITH CEDILLA
        || 'Č' --  200  12/08  310  C8  CAPITAL LETTER C WITH CARON
        || 'É' --  201  12/09  311  C9  CAPITAL LETTER E WITH ACUTE ACCENT
        || 'Ę' --  202  12/10  312  CA  CAPITAL LETTER E WITH OGONEK
        || 'Ë' --  203  12/11  313  CB  CAPITAL LETTER E WITH DIAERESIS
        || 'Ě' --  204  12/12  314  CC  CAPITAL LETTER E WITH CARON
        || 'Í' --  205  12/13  315  CD  CAPITAL LETTER I WITH ACUTE ACCENT
        || 'Î' --  206  12/14  316  CE  CAPITAL LETTER I WITH CIRCUMFLEX ACCENT
        || 'Ď' --  207  12/15  317  CF  CAPITAL LETTER D WITH CARON
        || 'Đ' --  208  13/00  320  D0  CAPITAL LETTER D WITH STROKE
        || 'Ń' --  209  13/01  321  D1  CAPITAL LETTER N WITH ACUTE ACCENT
        || 'Ň' --  210  13/02  322  D2  CAPITAL LETTER N WITH CARON
        || 'Ó' --  211  13/03  323  D3  CAPITAL LETTER O WITH ACUTE ACCENT
        || 'Ô' --  212  13/04  324  D4  CAPITAL LETTER O WITH CIRCUMFLEX
        || 'Ő' --  213  13/05  325  D5  CAPITAL LETTER O WITH DOUBLE ACUTE ACCENT
        || 'Ö' --  214  13/06  326  D6  CAPITAL LETTER O WITH DIAERESIS
        || '×' --  215  13/07  327  D7  MULTIPLICATION SIGN
        || 'Ř' --  216  13/08  330  D8  CAPITAL LETTER R WITH CARON
        || 'Ů' --  217  13/09  331  D9  CAPITAL LETTER U WITH RING ABOVE
        || 'Ú' --  218  13/10  332  DA  CAPITAL LETTER U WITH ACUTE ACCENT
        || 'Ű' --  219  13/11  333  DB  CAPITAL LETTER U WITH DOUBLE ACUTE ACCENT
        || 'Ü' --  220  13/12  334  DC  CAPITAL LETTER U WITH DIAERESIS
        || 'Ý' --  221  13/13  335  DD  CAPITAL LETTER Y WITH ACUTE ACCENT
        || 'Ţ' --  222  13/14  336  DE  CAPITAL LETTER T WITH CEDILLA
        || 'ß' --  223  13/15  337  DF  SMALL GERMAN LETTER SHARP s
        || 'ŕ' --  224  14/00  340  E0  SMALL LETTER R WITH ACUTE ACCENT
        || 'á' --  225  14/01  341  E1  SMALL LETTER A WITH ACUTE ACCENT
        || 'â' --  226  14/02  342  E2  SMALL LETTER A WITH CIRCUMFLEX
        || 'ă' --  227  14/03  343  E3  SMALL LETTER A WITH BREVE
        || 'ä' --  228  14/04  344  E4  SMALL LETTER A WITH DIAERESIS
        || 'ĺ' --  229  14/05  345  E5  SMALL LETTER L WITH ACUTE ACCENT
        || 'ć' --  230  14/06  346  E6  SMALL LETTER C WITH ACUTE ACCENT
        || 'ç' --  231  14/07  347  E7  SMALL LETTER C WITH CEDILLA
        || 'č' --  232  14/08  350  E8  SMALL LETTER C WITH CARON
        || 'é' --  233  14/09  351  E9  SMALL LETTER E WITH ACUTE ACCENT
        || 'ę' --  234  14/10  352  EA  SMALL LETTER E WITH OGONEK
        || 'ë' --  235  14/11  353  EB  SMALL LETTER E WITH DIAERESIS
        || 'ě' --  236  14/12  354  EC  SMALL LETTER E WITH CARON
        || 'í' --  237  14/13  355  ED  SMALL LETTER I WITH ACUTE ACCENT
        || 'î' --  238  14/14  356  EE  SMALL LETTER I WITH CIRCUMFLEX ACCENT
        || 'ď' --  239  14/15  357  EF  SMALL LETTER D WITH CARON
        || 'đ' --  240  15/00  360  F0  SMALL LETTER D WITH STROKE
        || 'ń' --  241  15/01  361  F1  SMALL LETTER N WITH ACUTE ACCENT
        || 'ň' --  242  15/02  362  F2  SMALL LETTER N WITH CARON
        || 'ó' --  243  15/03  363  F3  SMALL LETTER O WITH ACUTE ACCENT
        || 'ô' --  244  15/04  364  F4  SMALL LETTER O WITH CIRCUMFLEX
        || 'ő' --  245  15/05  365  F5  SMALL LETTER O WITH DOUBLE ACUTE ACCENT
        || 'ö' --  246  15/06  366  F6  SMALL LETTER O WITH DIAERESIS
        || '÷' --  247  15/07  367  F7  DIVISION SIGN
        || 'ř' --  248  15/08  370  F8  SMALL LETTER R WITH CARON
        || 'ů' --  249  15/09  371  F9  SMALL LETTER U WITH RING ABOVE
        || 'ú' --  250  15/10  372  FA  SMALL LETTER U WITH ACUTE ACCENT
        || 'ű' --  251  15/11  373  FB  SMALL LETTER U WITH DOUBLE ACUTE ACCENT
        || 'ü' --  252  15/12  374  FC  SMALL LETTER U WITH DIAERESIS
        || 'ý' --  253  15/13  375  FD  SMALL LETTER Y WITH ACUTE ACCENT
        || 'ţ' --  254  15/14  376  FE  SMALL LETTER T WITH CEDILLA
        || '˙' --  255  15/15  377  FF  DOT ABOVE
        ;

        b2 = rpad( '', v_step, v_text );

        while( n < k ) do
        begin
            b1 = b1 || b2;
            n = gen_id(g, v_step);
        end
        -- Result: length of `b1` is much more than 32 Kb (about 5e5 for single-byte and 1e6 for utf8 encoding)

        b2 = b1 || 'Ąňňö‡Đő×íńî';
        b1_octet_len=octet_length(b1);
        b2_octet_len=octet_length(b2);
        trimmed_octet_len=octet_length( trim(b1 from b2) );

        b1_char_len=char_length(b1);
        b2_char_len=char_length(b2);
        trimmed_char_len=char_length( trim(b1 from b2) );
        suspend;

    end
    ^
    set term ;^
"""

act = isql_act('db', test_script)

expected_stdout = """
	B1_OCTET_LEN                    1082024
	B2_OCTET_LEN                    1082047
	TRIMMED_OCTET_LEN               23
	B1_CHAR_LEN                     507780
	B2_CHAR_LEN                     507791
	TRIMMED_CHAR_LEN                11
"""

@pytest.mark.intl
@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(charset='utf8')
    assert act.clean_stdout == act.clean_expected_stdout

