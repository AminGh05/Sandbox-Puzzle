$env:PYTHONUNBUFFERED = '1'
Set-Location -LiteralPath $PSScriptRoot
& py -3.13 ".\train_heuristic.py" *> ".\train_log.txt"
Write-Output "training finished with exit code $LASTEXITCODE"
