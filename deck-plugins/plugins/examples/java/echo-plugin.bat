@echo off
REM Windows launcher — set entrypoint to ./echo-plugin.bat on Windows builds.
java -cp "%~dp0echo-plugin.jar;%~dp0gson.jar" com.example.echo.EchoPlugin
