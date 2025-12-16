; NSIS installer script for open-in-mpv
; This installer will:
; - Install the PyInstaller-built EXE
; - Download and install mpv.exe
; - Install native messaging JSON files for detected browsers

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "StrFunc.nsh"

; Initialize StrRep function
${StrRep}

; Application information
!define APP_NAME "open-in-mpv"
!define APP_VERSION "0.1.3"
!define APP_PUBLISHER "Tatsh"
!define APP_URL "https://github.com/${APP_PUBLISHER}/${APP_NAME}"
!define APP_EXEC "${APP_NAME}.exe"
!define MPV_VERSION "20251214-git-f7be2ee"
!define MPV_DOWNLOAD_URL "https://downloads.sourceforge.net/project/mpv-player-windows/64bit/mpv-x86_64-${MPV_VERSION}.7z"
!define MPV_INSTALL_URL "https://mpv.io/installation/"
!define YTDLP_VERSION "2025.12.08"
!define YTDLP_DOWNLOAD_URL "https://github.com/yt-dlp/yt-dlp/releases/download/${YTDLP_VERSION}/yt-dlp.exe"

; Determine current year
!define /date CURRENT_YEAR "%Y"

; Installer configuration
Name "${APP_NAME} ${APP_VERSION}"
OutFile "${APP_NAME}-${APP_VERSION}-setup.exe"
InstallDir "$LOCALAPPDATA\${APP_NAME}"
RequestExecutionLevel user
ManifestDPIAware true

; Interface configuration
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Version information
VIProductVersion "0.1.3.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "LegalCopyright" "Copyright (c) ${CURRENT_YEAR} ${APP_PUBLISHER}."

Section "Install" SecInstall
  SetOutPath "$INSTDIR"

  ; Install the main executable
  File "dist\${APP_EXEC}"

  ; Check if mpv.exe already exists
  DetailPrint "Checking for mpv.exe..."
  IfFileExists "$INSTDIR\mpv.exe" mpv_exists mpv_not_found

  mpv_exists:
    DetailPrint "mpv.exe already present."
    Goto mpv_done

  mpv_not_found:
    ; Download mpv immediately
    DetailPrint "Downloading mpv from ${MPV_DOWNLOAD_URL}..."
    inetc::get /TIMEOUT=30000 "${MPV_DOWNLOAD_URL}" "$TEMP\mpv.7z" /END
    Pop $0
    ${If} $0 == "OK"
      DetailPrint "Extracting mpv files..."
      ; Extract 7z archive to temporary directory
      SetOutPath "$TEMP\mpv-extract"
      Nsis7z::ExtractWithDetails "$TEMP\mpv.7z" "Extracting mpv files %s..."
      ; Copy expected files to installation directory
      DetailPrint "Installing mpv files..."
      CopyFiles "$TEMP\mpv-extract\mpv.exe" "$INSTDIR\mpv.exe"
      CopyFiles "$TEMP\mpv-extract\mpv.com" "$INSTDIR\mpv.com"
      CopyFiles "$TEMP\mpv-extract\d3dcompiler_43.dll" "$INSTDIR\d3dcompiler_43.dll"
      CopyFiles /SILENT "$TEMP\mpv-extract\mpv" "$INSTDIR\mpv"
      ; Clean up temporary extraction directory
      RMDir /r "$TEMP\mpv-extract"
      DetailPrint "mpv files installed."
    ${Else}
      DetailPrint "Failed to download mpv. Opening download page..."
      ExecShell "open" "${MPV_INSTALL_URL}"
      MessageBox MB_OK "Please download mpv manually and place mpv.exe in:$\n$INSTDIR"
    ${EndIf}

  mpv_done:

  ; Check if yt-dlp.exe already exists
  DetailPrint "Checking for yt-dlp.exe..."
  IfFileExists "$INSTDIR\yt-dlp.exe" ytdlp_exists ytdlp_not_found

  ytdlp_exists:
    DetailPrint "yt-dlp.exe already present."
    Goto ytdlp_done

  ytdlp_not_found:
    ; Download yt-dlp immediately
    DetailPrint "Downloading yt-dlp from ${YTDLP_DOWNLOAD_URL}..."
    inetc::get /TIMEOUT=30000 "${YTDLP_DOWNLOAD_URL}" "$INSTDIR\yt-dlp.exe" /END
    Pop $0
    ${If} $0 == "OK"
      DetailPrint "yt-dlp downloaded successfully."
    ${Else}
      DetailPrint "Failed to download yt-dlp. Continuing without it..."
    ${EndIf}

  ytdlp_done:

  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Write registry keys for uninstaller
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${APP_EXEC}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"

  ; Install native messaging host manifest
  Call WriteHostJSON

  ; Install native messaging hosts for detected browsers via registry
  Call InstallNativeMessagingHosts

SectionEnd

Function WriteHostJSON
  ; Create the JSON file with proper escaping for the path
  StrCpy $1 "$INSTDIR\${APP_EXEC}"
  ; Replace single backslashes with double backslashes for JSON
  ${StrRep} $2 $1 "\" "\\"

  FileOpen $0 "$INSTDIR\sh.tat.open_in_mpv.json" w
  FileWrite $0 '{$\r$\n'
  FileWrite $0 '  "allowed_origins": ["chrome-extension://jlhcojdohadhkchjpjefbmagpiaedpgc/"],$\r$\n'
  FileWrite $0 '  "description": "Opens a URL in mpv (for use with extension).",$\r$\n'
  FileWrite $0 '  "name": "sh.tat.open_in_mpv",$\r$\n'
  FileWrite $0 '  "path": "$2",$\r$\n'
  FileWrite $0 '  "type": "stdio"$\r$\n'
  FileWrite $0 '}$\r$\n'
  FileClose $0
FunctionEnd

Function InstallNativeMessagingHosts
  ; Chrome
  IfFileExists "$LOCALAPPDATA\Google\Chrome\*.*" 0 +3
    DetailPrint "Installing native messaging host for Google Chrome..."
    Call InstallChromeHost

  ; Chrome Beta
  IfFileExists "$LOCALAPPDATA\Google\Chrome Beta\*.*" 0 +3
    DetailPrint "Installing native messaging host for Google Chrome Beta..."
    Call InstallChromeBetaHost

  ; Chrome Canary
  IfFileExists "$LOCALAPPDATA\Google\Chrome SxS\*.*" 0 +3
    DetailPrint "Installing native messaging host for Google Chrome Canary..."
    Call InstallChromeCanaryHost

  ; Chromium
  IfFileExists "$LOCALAPPDATA\Chromium\*.*" 0 +3
    DetailPrint "Installing native messaging host for Chromium..."
    Call InstallChromiumHost

  ; Firefox
  IfFileExists "$APPDATA\Mozilla\Firefox\*.*" 0 +3
    DetailPrint "Installing native messaging host for Firefox..."
    Call InstallFirefoxHost

FunctionEnd

Function InstallChromeHost
  WriteRegStr HKCU "Software\Google\Chrome\NativeMessagingHosts\sh.tat.open_in_mpv" "" "$INSTDIR\sh.tat.open_in_mpv.json"
FunctionEnd

Function InstallChromeBetaHost
  WriteRegStr HKCU "Software\Google\Chrome Beta\NativeMessagingHosts\sh.tat.open_in_mpv" "" "$INSTDIR\sh.tat.open_in_mpv.json"
FunctionEnd

Function InstallChromeCanaryHost
  WriteRegStr HKCU "Software\Google\Chrome Canary\NativeMessagingHosts\sh.tat.open_in_mpv" "" "$INSTDIR\sh.tat.open_in_mpv.json"
FunctionEnd

Function InstallChromiumHost
  WriteRegStr HKCU "Software\Chromium\NativeMessagingHosts\sh.tat.open_in_mpv" "" "$INSTDIR\sh.tat.open_in_mpv.json"
FunctionEnd

Function InstallFirefoxHost
  WriteRegStr HKCU "SOFTWARE\Mozilla\NativeMessagingHosts\sh.tat.open_in_mpv" "" "$INSTDIR\sh.tat.open_in_mpv.json"
FunctionEnd

Section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\${APP_EXEC}"
  Delete "$INSTDIR\mpv.exe"
  Delete "$INSTDIR\mpv.com"
  Delete "$INSTDIR\d3dcompiler_43.dll"
  Delete "$INSTDIR\yt-dlp.exe"
  Delete "$INSTDIR\sh.tat.open_in_mpv.json"
  Delete "$INSTDIR\Uninstall.exe"

  ; Remove mpv directory
  RMDir /r "$INSTDIR\mpv"

  ; Remove native messaging host registry entries
  DeleteRegKey HKCU "Software\Google\Chrome\NativeMessagingHosts\sh.tat.open_in_mpv"
  DeleteRegKey HKCU "Software\Google\Chrome Beta\NativeMessagingHosts\sh.tat.open_in_mpv"
  DeleteRegKey HKCU "Software\Google\Chrome Canary\NativeMessagingHosts\sh.tat.open_in_mpv"
  DeleteRegKey HKCU "Software\Chromium\NativeMessagingHosts\sh.tat.open_in_mpv"
  DeleteRegKey HKCU "SOFTWARE\Mozilla\NativeMessagingHosts\sh.tat.open_in_mpv"

  ; Remove directories if empty
  RMDir "$INSTDIR"

  ; Remove registry keys
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SectionEnd
