#coding:utf-8

"""
ID:          issue-4022
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/4022
TITLE:       computed index by SUBSTRING function for long columns
DESCRIPTION:
JIRA:        CORE-3672
NOTES:
    [12.04.2026] pzotov
    Totally re-implemented. Use all avaliable (currently) value of page_size: 86; 16k and 32k (for 4.x+).
    For every tested page size a table is created with text column of size = 8190 characters (using charset = 'utf8').
    Maximal length of index key for uniode characters that require (commonly) up to 6 bytes per character is:
        max_idx_key = int( (page_size / 4 - 9) / UTF_BYTES_PER_CHAR )
    We add <ROWS_TO_CHECK> randomly generated unicode strings to the table and then create COMPUTED-BY index
    with expression that is defined by: substring(<col> from 1 for {max_idx_key}).
    After this we run query 'select min(<col>) from ...' which must involve in use just created index.
    Query statistics must show that number of natural reads are zero and indexed reads only did occur.
    Also, obtained value of <col> must be equal to minimal value of array that stored added values (SortedList).
    If all checks passed then NO output must be as reault of this test.

    Checked on 6.0.0.1891; 5.0.4.1808; 4.0.7.3269; 3.0.14.33855.
"""
import os
import random
from pathlib import Path
from sortedcontainers import SortedList
from firebird.driver import DatabaseError, driver_config, create_database

import pytest
from firebird.qa import *

UTF_BYTES_PER_CHAR = 6
ROWS_TO_CHECK = 50

db = db_factory(charset = 'utf8')
act = python_act('db')
tmp_fdb = temp_file('tmp_3672_diff_page_size.fdb')

#-----------------------------------------------------------

def get_random_unicode(length):

    # https://jrgraphix.net/r/Unicode/
    UNICODE_RANGES_MAP = {
        (0x0028, 0x007E) : 'Basic Latin WITHOUT apostrophe and control character <DELETE>, 0x7F',
        (0x00A0, 0x00FF) : 'Latin-1 Supplement',
        (0x0100, 0x017F) : 'Latin Extended-A',
        (0x0180, 0x024F) : 'Latin Extended-B',
        (0x0400, 0x04FF) : 'Cyrillic',
        (0x0500, 0x052F) : 'Cyrillic Supplementary',
        (0x0300, 0x036F) : 'Combining Diacritical Marks',
        (0x0250, 0x02AF) : 'IPA Extensions',
        (0x0370, 0x03FF) : 'Greek and Coptic',
        (0x0530, 0x058F) : 'Armenian',
        (0x02B0, 0x02FF) : 'Spacing Modifier Letters',
        (0x0590, 0x05FF) : 'Hebrew',
        (0x0600, 0x06FF) : 'Arabic',
        (0x0700, 0x074F) : 'Syriac',
        (0x0780, 0x07BF) : 'Thaana',
        (0x0900, 0x097F) : 'Devanagari',
        (0x0980, 0x09FF) : 'Bengali',
        (0x0A00, 0x0A7F) : 'Gurmukhi',
        (0x0A80, 0x0AFF) : 'Gujarati',
        (0x0B00, 0x0B7F) : 'Oriya',
        (0x0B80, 0x0BFF) : 'Tamil',
        (0x0C00, 0x0C7F) : 'Telugu',
        (0x0C80, 0x0CFF) : 'Kannada',
        (0x0D00, 0x0D7F) : 'Malayalam',
        (0x0D80, 0x0DFF) : 'Sinhala',
        (0x0E00, 0x0E7F) : 'Thai',
        (0x0E80, 0x0EFF) : 'Lao',
        (0x0F00, 0x0FFF) : 'Tibetan',
        (0x1000, 0x109F) : 'Myanmar',
        (0x10A0, 0x10FF) : 'Georgian',
        (0x1100, 0x11FF) : 'Hangul Jamo',
        (0x1200, 0x137F) : 'Ethiopic',
        (0x13A0, 0x13FF) : 'Cherokee',
        (0x1400, 0x167F) : 'Unified Canadian Aboriginal Syllabics',
        (0x1680, 0x169F) : 'Ogham',
        (0x16A0, 0x16FF) : 'Runic',
        (0x1700, 0x171F) : 'Tagalog',
        (0x1720, 0x173F) : 'Hanunoo',
        (0x1740, 0x175F) : 'Buhid',
        (0x1760, 0x177F) : 'Tagbanwa',
        (0x1780, 0x17FF) : 'Khmer',
        (0x1800, 0x18AF) : 'Mongolian',
        (0x1900, 0x194F) : 'Limbu',
        (0x1950, 0x197F) : 'Tai Le',
        (0x19E0, 0x19FF) : 'Khmer Symbols',
        (0x1D00, 0x1D7F) : 'Phonetic Extensions',
        (0x1E00, 0x1EFF) : 'Latin Extended Additional',
        (0x1F00, 0x1FFF) : 'Greek Extended',
        (0x2000, 0x206F) : 'General Punctuation',
        (0x2070, 0x209F) : 'Superscripts and Subscripts',
        (0x20A0, 0x20CF) : 'Currency Symbols',
        (0x20D0, 0x20FF) : 'Combining Diacritical Marks for Symbols',
        (0x2100, 0x214F) : 'Letterlike Symbols',
        (0x2150, 0x218F) : 'Number Forms',
        (0x2190, 0x21FF) : 'Arrows',
        (0x2200, 0x22FF) : 'Mathematical Operators',
        (0x2300, 0x23FF) : 'Miscellaneous Technical',
        (0x2400, 0x243F) : 'Control Pictures',
        (0x2440, 0x245F) : 'Optical Character Recognition',
        (0x2460, 0x24FF) : 'Enclosed Alphanumerics',
        (0x2500, 0x257F) : 'Box Drawing',
        (0x2580, 0x259F) : 'Block Elements',
        (0x25A0, 0x25FF) : 'Geometric Shapes',
        (0x2600, 0x26FF) : 'Miscellaneous Symbols',
        (0x2700, 0x27BF) : 'Dingbats',
        (0x27C0, 0x27EF) : 'Miscellaneous Mathematical Symbols-A',
        (0x27F0, 0x27FF) : 'Supplemental Arrows-A',
        (0x2800, 0x28FF) : 'Braille Patterns',
        (0x2900, 0x297F) : 'Supplemental Arrows-B',
        (0x2980, 0x29FF) : 'Miscellaneous Mathematical Symbols-B',
        (0x2A00, 0x2AFF) : 'Supplemental Mathematical Operators',
        (0x2B00, 0x2BFF) : 'Miscellaneous Symbols and Arrows',
        (0x2E80, 0x2EFF) : 'CJK Radicals Supplement',
        (0x2F00, 0x2FDF) : 'Kangxi Radicals',
        (0x2FF0, 0x2FFF) : 'Ideographic Description Characters',
        (0x3000, 0x303F) : 'CJK Symbols and Punctuation',
        (0x3040, 0x309F) : 'Hiragana',
        (0x30A0, 0x30FF) : 'Katakana',
        (0x3100, 0x312F) : 'Bopomofo',
        (0x3130, 0x318F) : 'Hangul Compatibility Jamo',
        (0x3190, 0x319F) : 'Kanbun',
        (0x31A0, 0x31BF) : 'Bopomofo Extended',
        (0x31F0, 0x31FF) : 'Katakana Phonetic Extensions',
        (0x3200, 0x32FF) : 'Enclosed CJK Letters and Months',
        (0x3300, 0x33FF) : 'CJK Compatibility',
        (0x3400, 0x4DBF) : 'CJK Unified Ideographs Extension A',
        (0x4DC0, 0x4DFF) : 'Yijing Hexagram Symbols',
        (0x4E00, 0x9FFF) : 'CJK Unified Ideographs',
        (0xA000, 0xA48F) : 'Yi Syllables',
        (0xA490, 0xA4CF) : 'Yi Radicals',
        (0xAC00, 0xD7AF) : 'Hangul Syllables',
        (0xE000, 0xF8FF) : 'Private Use Area',
        (0xF900, 0xFAFF) : 'CJK Compatibility Ideographs',
        (0xFB00, 0xFB4F) : 'Alphabetic Presentation Forms',
        (0xFB50, 0xFDFF) : 'Arabic Presentation Forms-A',
        (0xFE00, 0xFE0F) : 'Variation Selectors',
        (0xFE20, 0xFE2F) : 'Combining Half Marks',
        (0xFE30, 0xFE4F) : 'CJK Compatibility Forms',
        (0xFE50, 0xFE6F) : 'Small Form Variants',
        (0xFE70, 0xFEFF) : 'Arabic Presentation Forms-B',
        (0xFF00, 0xFFEF) : 'Halfwidth and Fullwidth Forms',
        (0xFFF0, 0xFFFF) : 'Specials',
        (0x10000, 0x1007F) : 'Linear B Syllabary',
        (0x10080, 0x100FF) : 'Linear B Ideograms',
        (0x10100, 0x1013F) : 'Aegean Numbers',
        (0x10300, 0x1032F) : 'Old Italic',
        (0x10330, 0x1034F) : 'Gothic',
        (0x10380, 0x1039F) : 'Ugaritic',
        (0x10400, 0x1044F) : 'Deseret',
        (0x10450, 0x1047F) : 'Shavian',
        (0x10480, 0x104AF) : 'Osmanya',
        (0x10800, 0x1083F) : 'Cypriot Syllabary',
        (0x1D000, 0x1D0FF) : 'Byzantine Musical Symbols',
        (0x1D100, 0x1D1FF) : 'Musical Symbols',
        (0x1D300, 0x1D35F) : 'Tai Xuan Jing Symbols',
        (0x1D400, 0x1D7FF) : 'Mathematical Alphanumeric Symbols',
        (0x20000, 0x2A6DF) : 'CJK Unified Ideographs Extension B',
        (0x2F800, 0x2FA1F) : 'CJK Compatibility Ideographs Supplement',
        (0xE0000, 0xE007F) : 'Tags',
    }

    alphabet = [
        chr(code_point) for current_range in UNICODE_RANGES_MAP.keys()
            for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return ''.join(random.choice(alphabet) for i in range(length))


#-----------------------------------------------------------

@pytest.mark.version('>=3')
def test_1(act: Action, tmp_fdb: Path, capsys):

    SCHEMA_PREFIX = '' if act.is_version('<6') else 'PUBLIC.'

    PAGE_SIZE_SET = [8192, 16384,]
    if act.is_version('<4'):
        pass
    else:
        PAGE_SIZE_SET.append(32768,)

    for pg_checked in PAGE_SIZE_SET:
        db_cfg_name = f'tmp_core_3672_page_{pg_checked}'
        db_cfg_object = driver_config.register_database(name = db_cfg_name)
        db_cfg_object.database.value = str(tmp_fdb)
        db_cfg_object.page_size.value = pg_checked

        try:
            tmp_fdb.unlink(missing_ok = True)
            test_rel_id = -1
            with create_database(db_cfg_name, charset = 'utf8') as con:
                con.execute_immediate('recreate table test(col1 varchar(8190))')
                con.commit()

                cur = con.cursor()
                cur.execute("select mon$page_size as pg_actual, r.rdb$relation_id as test_rel_id from mon$database d left join rdb$relations r on r.rdb$relation_name=upper('test')")
                pg_actual, test_rel_id = cur.fetchone()[:2]

                assert pg_checked == pg_actual, f'mon$page_size = {pg_actual} not equals to expected {pg_checked=}'
                assert test_rel_id > 0, f'could not find test table name in rdb$relations'

                #############################################################
                max_idx_key = int( (pg_actual / 4 - 9) / UTF_BYTES_PER_CHAR ) 
                #############################################################
                ps, rs = None, None
                try:
                    ps = cur.prepare('insert into test(col1) values(?)')
                    ss = SortedList()
                    for i in range(ROWS_TO_CHECK):
                        long_utf8_data = ''.join(set(get_random_unicode( max_idx_key + 1 )))
                        cur.execute(ps, (long_utf8_data,))
                        ss.add(long_utf8_data)
                    con.commit()

                    con.execute_immediate(f'create index test_col1_expr on test computed by ( substring(col1 from 1 for {max_idx_key}) )')
                    con.commit()

                    tabstat1 = [ p for p in con.info.get_table_access_stats() if p.table_id == test_rel_id ]

                    min_fetched = '<undefined>'
                    cur.execute(f'select min(substring(col1 from 1 for {max_idx_key})) from test')
                    for r in cur:
                        min_fetched = r[0]
                    
                    tabstat2 = [ p for p in con.info.get_table_access_stats() if p.table_id == test_rel_id ]

                    nat_reads = (tabstat2[0].sequential if tabstat2[0].sequential else 0) - (tabstat1[0].sequential if tabstat1[0].sequential else 0)
                    idx_reads = (tabstat2[0].indexed if tabstat2[0].indexed else 0) - (tabstat1[0].indexed if tabstat1[0].indexed else 0)
                    
                    if nat_reads == 0 and idx_reads > 0 and (min_fetched == ss[0][:max_idx_key]):
                        # MIN() value has been obtained using INDEX and matches to checked one.
                        # EXPECTED. NOTHING TO PRINT.
                        pass
                    else:
                        print(f'UNEXPECTED STATISTICS AND/OR QUERY RESULT: {pg_actual=}: {nat_reads=}, {idx_reads=}; min_fetched == 1st of SortedList() ? => ', min_fetched == ss[0][:max_idx_key])

                except DatabaseError as e:
                    print( e.__str__() )
                    print(e.gds_codes)
                finally:
                    if rs:
                        rs.close() # <<< EXPLICITLY CLOSING CURSOR RESULTS
                    if ps:
                        ps.free()

        except DatabaseError as e:
            print( e.__str__() )
            print(e.gds_codes)


    expected_stdout = f"""
    """

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
