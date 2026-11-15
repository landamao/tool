@echo off
powershell -Command "Get-FileHash '%1' -Algorithm MD5 | Format-List"