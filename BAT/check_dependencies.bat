@echo off
echo === Checking and Installing Python Dependencies ===
echo.

REM Activate virtual environment
echo Activating virtual environment...
call env\Scripts\activate.bat

REM Check Python version
echo.
echo Python version:
python --version

REM Check pip version  
echo.
echo Pip version:
pip --version

REM Upgrade pip first
echo.
echo Upgrading pip...
pip install --upgrade pip

REM Install backend dependencies
echo.
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt

REM Check installed packages
echo.
echo Installed packages:
pip list

REM Test imports
echo.
echo Testing critical imports...
python -c "import fastapi; print('✓ FastAPI imported successfully')"
python -c "import linebot; print('✓ LINE Bot SDK imported successfully')"
python -c "import langchain; print('✓ LangChain imported successfully')"
python -c "import sqlalchemy; print('✓ SQLAlchemy imported successfully')"

echo.
echo === Dependency check completed ===
pause
