$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$outputDir = Join-Path $projectRoot "ga_evaluation"
python (Join-Path $projectRoot "evaluate_genetic.py") `
    --trials 100 `
    --seed 20261127 `
    --population-size 60 `
    --sequence-length 30 `
    --generations 200 `
    --output-dir $outputDir

if ($LASTEXITCODE -ne 0) {
    throw "GA evaluation failed with exit code $LASTEXITCODE"
}
