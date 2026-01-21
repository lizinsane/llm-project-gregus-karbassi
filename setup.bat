@echo off
REM Swiss History RAG - Setup Script for Windows

echo Swiss History RAG - Setup Script
echo ======================================
echo.

REM Check Python version
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo WARNING: Please edit .env and add your API keys!
)

REM Create necessary directories
echo.
echo Creating necessary directories...
python -c "from src.utils import ensure_directories; ensure_directories()"

REM Test configuration
echo.
echo Testing configuration...
python src/utils.py

echo.
echo ======================================
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file and add your API keys
echo 2. Place your PDF in data/raw/ directory
echo 3. Run: python src/ingestion/pdf_processor.py (Phase 2)
echo 4. Run: streamlit run src/web/app.py (Phase 4)
echo.
echo To activate the environment later, run:
echo   venv\Scripts\activate.bat
echo.

pause
