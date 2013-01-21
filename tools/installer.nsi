;Coinbox Windows installer script
;Modified by Dustin Spicuzza
;Based on the Quod Libet / Ex Falso Windows installer script
;Modified by Steven Robertson
;Based on the NSIS Modern User Interface Start Menu Folder Example Script
;Written by Joost Verburg

    ;compression
    SetCompressor /SOLID LZMA

    !define MULTIUSER_EXECUTIONLEVEL Highest
    !define MULTIUSER_MUI
    !define MULTIUSER_INSTALLMODE_COMMANDLINE
    !include "MultiUser.nsh"

    !define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\Coinbox"
    !define INSTDIR_KEY "Software\Coinbox"
    !define INSTDIR_SUBKEY "InstDir"

;--------------------------------
;Include Modern UI and other libs

    !include "MUI2.nsh"
    !include "LogicLib.nsh"

;--------------------------------
;General

    ;Name and file
    Name "Coinbox"
    OutFile "coinbox-install.exe"

    ;Default installation folder
    InstallDir "$PROGRAMFILES\Coinbox"

    ;Request application privileges for Windows Vista+
    RequestExecutionLevel admin

;--------------------------------
;Variables

    Var StartMenuFolder
    Var instdir_temp

;--------------------------------
;Interface Settings

    !define MUI_ABORTWARNING
    !define MUI_ICON "dist\coinbox\coinbox.ico"
  
;--------------------------------
;Pages

    !insertmacro MULTIUSER_PAGE_INSTALLMODE
    !insertmacro MUI_PAGE_LICENSE "dist\coinbox\COPYING"
    !insertmacro MUI_PAGE_DIRECTORY

    ;Start Menu Folder Page Configuration
    !define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
    !define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\Coinbox" 
    !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "StartMenuFolder"

    !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

    !insertmacro MUI_PAGE_INSTFILES

    !insertmacro MUI_UNPAGE_CONFIRM
    !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

    !insertmacro MUI_LANGUAGE "English" ;first language is the default language

;------------------------------------------------------------
; Install Coinbox

Section "-Coinbox" SecCoinbox

    SetOutPath "$INSTDIR"

    File /r "dist\coinbox\*.*" 

    ;Store installation folder
    WriteRegStr SHCTX "${INSTDIR_KEY}" "${INSTDIR_SUBKEY}" $INSTDIR

    ;Multi user uninstaller stuff
    WriteRegStr SHCTX "${UNINST_KEY}" \
    "DisplayName" "Coinbox POS"
    WriteRegStr SHCTX "${UNINST_KEY}" "DisplayIcon" "$\"$INSTDIR\coinbox.ico$\""
    WriteRegStr SHCTX "${UNINST_KEY}" "UninstallString" \
    "$\"$INSTDIR\uninstall.exe$\" /$MultiUser.InstallMode"
    WriteRegStr SHCTX "${UNINST_KEY}" "QuietUninstallString" \
    "$\"$INSTDIR\uninstall.exe$\" /$MultiUser.InstallMode /S"

    ;Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"

    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application

    ;Create shortcuts
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Coinbox.lnk" "$INSTDIR\coinbox.exe" "" "$INSTDIR\coinbox.ico"

    !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

Function .onInit
    !insertmacro MULTIUSER_INIT
    ;Read the install dir and set it
    ReadRegStr $instdir_temp SHCTX "${INSTDIR_KEY}" "${INSTDIR_SUBKEY}"
    StrCmp $instdir_temp "" skip 0
    StrCpy $INSTDIR $instdir_temp
    skip:
    
FunctionEnd

Function .onGUIEnd

FunctionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

    RMDir /r "$INSTDIR"

    Delete "$INSTDIR\uninstall.exe"

    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder

    Delete "$SMPROGRAMS\$StartMenuFolder\Coinbox.lnk"
    RMDir "$SMPROGRAMS\$StartMenuFolder"

    DeleteRegKey SHCTX "${UNINST_KEY}"
    DeleteRegKey SHCTX "${INSTDIR_KEY}"

SectionEnd

Function un.onInit
    !insertmacro MULTIUSER_UNINIT
FunctionEnd
