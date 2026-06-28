# Start the CMIE Studio backend
# Run from project root: .\webapp\start-backend.ps1

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

& "$ProjectRoot\venv\Scripts\Activate.ps1"

uvicorn webapp.backend.main:app --host 0.0.0.0 --port 8000 --reload
