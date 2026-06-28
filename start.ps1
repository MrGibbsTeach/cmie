# CMIE Studio launcher
$root = $PSScriptRoot

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; & '.\venv\Scripts\Activate.ps1'; uvicorn webapp.backend.main:app --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\webapp\frontend'; npm run dev"

Start-Sleep 4
Start-Process "http://localhost:3001"
