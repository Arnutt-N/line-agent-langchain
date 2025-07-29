@echo off
echo ================================
echo Vercel Deployment Helper
echo ================================
echo.

echo [1/3] Checking if Vercel CLI is installed...
where vercel >nul 2>&1
if %errorlevel% neq 0 (
    echo Vercel CLI not found. Installing...
    npm install -g vercel
) else (
    echo Vercel CLI is already installed.
)

echo.
echo [2/3] Building frontend...
cd frontend
npm install
npm run build
cd ..

echo.
echo [3/3] Ready to deploy!
echo.
echo To deploy to Vercel, run:
echo   vercel --prod
echo.
echo Don't forget to:
echo 1. Set environment variables in Vercel Dashboard
echo 2. Update LINE Bot webhook URL after deployment
echo 3. Test the deployment
echo.

pause