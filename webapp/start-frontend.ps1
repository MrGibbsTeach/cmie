# Start the CMIE Studio frontend
# Run from project root: .\webapp\start-frontend.ps1

$FrontendDir = Join-Path $PSScriptRoot "frontend"
Set-Location $FrontendDir

npm run dev
