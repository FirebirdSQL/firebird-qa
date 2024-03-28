#coding:utf-8

"""
ID:          issue-5957
ISSUE:       5957
TITLE:       File description on Firebird executables should be specific
DESCRIPTION:
    ::: NB :::
    We can not obtain 'File description' property using Python.
    Also this property is not accessible for WMIC interface.
    For this reason it was decided to create on-the-fly Visual Basic script and process it by CSCRIPT.EXE utility
    which exists since 2000/XP on every Windows host in %System%\\system32\\ folder.
    VB script accepts full path and filename as single mandatory argument.
    We run this script for each widely-used FB binaries (executables and DLLs).
    Its output must contain only FILE name (w/o disk and path) and its 'File description' property value.
JIRA:        CORE-5691
FBTEST:      bugs.core_5691
NOTES:
    [29.11.2023] pzotov
    Checked on 6.0.0.157, 5.0.0.1280, 4.0.5.3031

    [28.03.2024] pzotov
    Added call os.system("chcp 65001") before invocation of VBS.
    This is needed on machine with non-ascii system locale, e.g. ru-ru etc (i.e. when chcp output is 866 or 1251).
    Otherwise VBS will not able to find attribute with name 'file description' (all of attributes will be returned in
    localized form).
"""
import os
from pathlib import Path
import subprocess
import time
import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[ ('[ \\t]+', ' '), ('\\(?\\d+([ ]|-)bit\\)?', '') ])

tmp_vbs = temp_file('tmp_5691.vbs')
tmp_log = temp_file('tmp_5691.log')

@pytest.mark.version('>=4.0')
@pytest.mark.platform('Windows')
def test_1(act: Action, tmp_vbs: Path, tmp_log: Path, capsys):

    # Get default value for 'Providers' parameter ("Remote,Engine13,Loopback"),
    # split it onto words and obtain name of 'engineNN':
    engine_version = 'UNDEFINED'
    with act.db.connect() as con:
        cur = con.cursor()
        # Remote, Engine13, Loopback
        cur.execute("select rdb$config_default from rdb$config where upper(rdb$config_name) = upper('Providers')")
        for r in cur:
            engine_version = [ p.lower().strip() for p in r[0].split(',') if p.lower().strip().startswith('engine'.lower()) ][0]

        assert 'engine'.lower() in engine_version

    vbs_source = """
        Option Explicit

        if wscript.arguments.count = 0 then
            wscript.echo "Missed fully qualified file name, i.e.: drive + path + file_name"
            wscript.quit
        end if

        dim fullname
        dim getDetails

        fullname = wscript.arguments(0)

        rem https://www.tek-tips.com/viewthread.cfm?qid=1402419

        getDetails = GetFileDetails( fullName )


        function GetFileDetails(fullName)

            on error resume next

            dim fso
            dim objFile

            set fso = CreateObject("Scripting.FileSystemObject")
            set objFile = fso.GetFile(fullName)

            if not fso.FileExists(fullName) Then
                wscript.echo "File '" & fullName & "' does not exist."
                wscript.Quit
            end if

            dim fileName
            dim folderName

            fileName = objFile.Name
            folderName = objFile.Path
            folderName = Left(folderName, Len(folderName)-Len(fileName))

            set objFile = Nothing
            set fso = Nothing

            dim objShell
            dim objFolder

            rem https://docs.microsoft.com/en-us/previous-versions/windows/desktop/legacy/bb776890(v=vs.85)
            rem The Windows Shell provides a powerful set of automation objects <...>
            rem You can use these objects to access <...> the file system, launch programs, and change system settings.

            set objShell = CreateObject("Shell.Application")
            set objFolder = objShell.NameSpace(folderName)

            dim i
            dim fdescr_idx
            dim propertyName

            i = 0
            fdescr_idx = 0
            do
                propertyName = vbNullString
                rem https://docs.microsoft.com/en-us/windows/win32/shell/folder-getdetailsof
                rem retrieves details about an item in a folder. for example, its size, type, or the time of its last modification.
                propertyName = objFolder.GetDetailsOf(objFolder.Items, i)
                if LCase(propertyName) = LCase("file description") then
                    fdescr_idx = i
                    exit do
                end if

                if propertyName = vbNullString then
                    exit do
                end if
                i = i + 1
            loop
            propertyName = Nothing
            rem wscript.echo "fdescr_idx=",fdescr_idx

            dim objFolderItem
            set objFolderItem = objFolder.ParseName(fileName)

            if (not objFolderItem Is Nothing) then
                dim attribName
                dim objInfo
                attribName = objFolder.GetDetailsOf(objFolder.Items, fdescr_idx)
                objInfo = objFolder.GetDetailsOf(objFolderItem, fdescr_idx)

                wscript.echo "'" & fileName & "' " & LCase(attribName) & ":", LCase(objInfo)

                attribName = Nothing
                objInfo = Nothing
            end if

            set objFolderItem = Nothing
            set objFolder = Nothing
            set objShell = Nothing
        end function
    """

    tmp_vbs.write_text(vbs_source)
    

    f_list = ( 'fbclient.dll',
               'gbak.exe',
               'gfix.exe',
               'gstat.exe',
               'fbguard.exe',
               'isql.exe',
               'fb_lock_print.exe',
               'firebird.exe',
               'nbackup.exe',
               'fbtracemgr.exe',
               'fbsvcmgr.exe',
               f'plugins/{engine_version}.dll',
               'plugins/legacy_auth.dll',
               'plugins/legacy_usermanager.dll',
               'plugins/srp.dll',
               'plugins/udr_engine.dll',
               'plugins/chacha.dll',
               'plugins/fbtrace.dll',
             )


    #for x in sorted(f_list):
    #    print(act.vars['bin-dir'] / x)

    # Following is needed on machine with non-ascii system locale, e.g. ru-ru etc (i.e. when chcp output is 866 or 1251).
    # Otherwise VBS will not able to find attribute with name 'file description' (all of attributes will be returned in
    # localized form).
    #
    os.system("chcp 65001")
    with open(tmp_log,'w') as vbs_log:
        for x in sorted(f_list):
            subprocess.call( [ 'cscript', '//nologo', str(tmp_vbs), act.vars['bin-dir'] / x  ], stdout = vbs_log, stderr = subprocess.STDOUT)


    with open( tmp_log,'r') as f:
        for line in f:
            print( line.lower() )

    expected_stdout = f"""
        'fb_lock_print.exe' 		file description: firebird lock print tool
        'fbclient.dll' 				file description: firebird client library
        'fbguard.exe' 				file description: firebird guardian
        'fbsvcmgr.exe' 				file description: firebird services management tool
        'fbtracemgr.exe' 			file description: firebird trace management tool
        'firebird.exe' 				file description: firebird server executable
        'gbak.exe' 					file description: firebird gbak tool
        'gfix.exe' 					file description: firebird gfix tool
        'gstat.exe' 				file description: firebird gstat tool
        'isql.exe' 					file description: firebird interactive query tool
        'nbackup.exe' 				file description: firebird physical backup management tool
        'chacha.dll' 				file description: firebird wire encryption plugin using chacha cypher
        '{engine_version}.dll'		file description: firebird engine plugin
        'fbtrace.dll' 				file description: firebird trace plugin
        'legacy_auth.dll' 			file description: firebird legacy auth plugin
        'legacy_usermanager.dll' 	file description: firebird legacy user manager plugin
        'srp.dll' 					file description: firebird srp user manager plugin
        'udr_engine.dll' 			file description: firebird user defined routines engine
    """

    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
