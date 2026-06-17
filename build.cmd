@echo off
setlocal
cd /d %~dp0

if not exist Build mkdir Build

echo === convert map ===
python Source\Tools\map_tools.py Assets\Original\MAPS\SKIRMISH.MX2
if errorlevel 1 goto :err

echo === generate viewport pack ===
python Source\Tools\viewport_pack.py
if errorlevel 1 goto :err

echo === generate SPI object packs ===
python Source\Tools\object_spi_pack.py
if errorlevel 1 goto :err

echo === disable DXT L4 scroll background ===
python Source\Tools\dxt_l4_scroll_buffer.py --disable
if errorlevel 1 goto :err

if "%HMM2_DYNAMIC_ACTOR%"=="1" (
  echo === generate dynamic actor ===
  python Source\Tools\dynamic_actor.py
  if errorlevel 1 goto :err
)

echo === generate scale table ===
python Source\Tools\gen_scale_table.py
if errorlevel 1 goto :err

if "%SJASMPLUS%"=="" set SJASMPLUS=C:\z80\tsconf_project\exe\sjasmplus\sjasmplus.exe
if "%SPGBLD%"=="" set SPGBLD=C:\z80\tsconf_project\exe\spgbld\spgbld.exe

if not exist "%SJASMPLUS%" (
  echo SJASMPLUS not found.
  echo Set SJASMPLUS to sjasmplus.exe path.
  exit /b 1
)

if not exist "%SPGBLD%" (
  echo SPGBLD not found.
  echo Set SPGBLD to spgbld.exe path.
  exit /b 1
)

echo === sjasmplus ===
"%SJASMPLUS%" Source\ASM\main.asm --syntax=ab --lst=Build\hmm2.lst --sym=Build\hmm2.sym
if errorlevel 1 goto :err

echo === check RAM_G/RAM_DL usage ===
python Source\Tools\check_ramg_usage.py
if errorlevel 1 goto :err

echo === split core pages ===
python Source\Tools\split_core.py
if errorlevel 1 goto :err

echo === spgbld ===
"%SPGBLD%" -b spgbld_vdac2.ini Build\hmm2_vdac2.spg
if errorlevel 1 goto :err

echo === verify FT812/RAM_G/DL ===
python Source\Tools\verify_ft812_pipeline.py
if errorlevel 1 goto :err

echo === done ===
goto :eof

:err
echo BUILD OR VERIFY FAILED
exit /b 1
