# This file is part of open-in-mpv.
#
# Copyright 2020 Andrew Udvare
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

$rev_name = 'sh.tat.open_in_mpv'
$url_prefix = 'https://raw.githubusercontent.com/Tatsh/open-in-mpv/master/host'
$open_in_mpv_bin_dir = "${HOME}\AppData\Roaming\open-in-mpv"

$nmh_manifest_url = "${url_prefix}/${revName}.json.in"
$output = "${open_in_mpv_bin_dir}\${rev_name}.json.in"
$exe_json = "${open_in_mpv_bin_dir}\open-in-mpv.exe"
$exe = "${open_in_mpv_bin_dir}\open-in-mpv.exe"
(New-Object System.Net.WebClient).DownloadFile($nmh_manifest_url, $output)
Get-Content -Path $output | % { $_ -replace '@BINPATH@/open-in-mpv', `
  $exe_json } > "${open_in_mpv_bin_dir}\${rev_name}.json"
Remove-Item -Path $output
New-ItemProperty `
  -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\open-in-mpv.exe' `
  -Value $exe
New-ItemProperty `
  -Path 'HKCR:\Applications\open-in-mpv.exe' `
  -Name NoStartPage

New-ItemProperty `
  -Path 'HKCU:\Software\Google\Chrome\NativeMessagingHosts' `
  -Name $rev_name `
  -Value $output `
  -PropertyType String `
  -Force | Out-Null

New-Item -ItemType Directory `
  -Directory "${HOME}\AppData\Roaming\open-in-mpv"
$open_in_mpv_url = "${url_prefix}/open-in-mpv"
$output = "${open_in_mpv_bin_dir}open-in-mpv.py"
(New-Object System.Net.WebClient).DownloadFile($open_in_mpv_url, $output)
