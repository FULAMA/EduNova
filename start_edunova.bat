@echo off
 REM Script batch pour démarrer EduNova
 REM Backend : FastAPI sur 0.0.0.0:8017
 REM Frontend : Vite sur 127.0.0.1:5173

 echo ==========================================
 echo   EduNova - Script de démarrage
 echo ==========================================
 echo.

 set PROJECT_ROOT=F:\EduNova
 set FRONTEND_ROOT=%PROJECT_ROOT%\frontend
 set DB_PATH=%PROJECT_ROOT%\edunova_test.db

 REM Vérifier Python
echo [CHECK] Verification de Python...
python --version 2>nul | findstr "3.13" >nul
if %ERRORLEVEL% equ 0 (
    echo  [OK] Python 3.13 detecte
) else (
    echo  [ERREUR] Python 3.13 requis
    pause
    exit /b 1
)

 REM Vérifier Node.js
echo [CHECK] Verification de Node.js...
node --version 2>nul | findstr "v18" >nul
if %ERRORLEVEL% equ 0 (
    echo  [OK] Node.js 18+ detecte
) else (
    echo  [ERREUR] Node.js 18+ requis
    pause
    exit /b 1
)

echo.

 REM Créer la base temporaire si elle n'existe pas
echo [SETUP] Preparation de la base de donnees temporaire...
if not exist "%DB_PATH%" (
    type nul > "%DB_PATH%"
    echo  [OK] %DB_PATH% creee
) else (
    echo  [OK] %DB_PATH% existe deja
)

echo.
echo ==========================================
echo   Demarrage du backend FastAPI...
echo ==========================================
echo.
echo   URL du backend : http://127.0.0.1:8017
echo   URL Swagger   : http://127.0.0.1:8017/docs
echo.

 REM Démarrer le backend dans un nouveau terminal
start "EduNova Backend" cmd /k "cd /d %PROJECT_ROOT% && set EDUNOVA_DATABASE_PATH=%DB_PATH% && uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017 --reload"

 REM Attendre que le backend soit prêt
echo [WAIT] Attente du demarrage du backend...
timeout /t 3 /nobreak >nul

 REM Vérifier que le backend répond
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8017/health > %TEMP%\backend_check.txt
set /p HTTP_CODE=< %TEMP%\backend_check.txt
del %TEMP%\backend_check.txt

if "%HTTP_CODE%" == "200" (
    echo  [OK] Backend demarre avec succes sur http://127.0.0.1:8017
) else (
    echo  [AVERTISSEMENT] Backend non accessible (code: %HTTP_CODE%)
    echo  Veuillez verifier les logs du backend
)

echo.
echo ==========================================
echo   Demarrage du frontend Vite...
echo ==========================================
echo.
echo   URL du frontend : http://127.0.0.1:5173
echo.

 REM Créer le fichier .env si nécessaire
if not exist "%FRONTEND_ROOT%\.env" (
    echo VITE_API_URL=http://127.0.0.1:8017 > "%FRONTEND_ROOT%\.env"
    echo VITE_GOOGLE_CLIENT_ID= >> "%FRONTEND_ROOT%\.env"
    echo  [OK] Fichier .env cree
)

 REM Démarrer le frontend dans un nouveau terminal
start "EduNova Frontend" cmd /k "cd /d %FRONTEND_ROOT% && npm run dev"

 REM Attendre que le frontend soit prêt
echo [WAIT] Attente du demarrage du frontend...
timeout /t 5 /nobreak >nul

 REM Vérifier que le frontend répond
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:5173 > %TEMP%\frontend_check.txt
set /p HTTP_CODE=< %TEMP%\frontend_check.txt
del %TEMP%\frontend_check.txt

if "%HTTP_CODE%" == "200" (
    echo  [OK] Frontend demarre avec succes sur http://127.0.0.1:5173
) else (
    echo  [AVERTISSEMENT] Frontend non accessible (code: %HTTP_CODE%)
    echo  Cela peut etre normal si Vite est encore en train de compiler
)

echo.
echo ==========================================
echo   ✅ EduNova est pret !
echo ==========================================
echo.
echo   Backend  : http://127.0.0.1:8017
echo   Frontend : http://127.0.0.1:5173
echo   Swagger  : http://127.0.0.1:8017/docs
echo.
echo   Ouvrez votre navigateur a : http://127.0.0.1:5173
echo.
echo   Pour arreter : Fermez les fenetres du backend et du frontend
echo.

pause
