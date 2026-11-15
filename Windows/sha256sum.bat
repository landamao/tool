@echo off
powershell -Command "Get-FileHash '%1' -Algorithm SHA256 | Format-List"