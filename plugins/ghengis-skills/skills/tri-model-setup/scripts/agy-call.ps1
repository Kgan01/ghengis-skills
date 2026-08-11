# agy-call.ps1 — thin wrapper for the Gemini leg of the tri-model harness.
# Shells to Google's Antigravity CLI (agy) non-interactively, logs every call
# to ~/.claude/tri-model/agy-usage.jsonl so the Ultra-vs-Pro decision has data.
#
# Usage:
#   agy-call.ps1 -Prompt "question"                    # default: flash
#   agy-call.ps1 -Prompt "question" -Model pro         # escalate deliberately
#   agy-call.ps1 -Prompt "q" -Cwd Y:\some\repo         # give agy a workspace
#   agy-call.ps1 -PromptFile path\to\prompt.md         # long prompts via file
param(
    [string]$Prompt,
    [string]$PromptFile,
    [string]$Model = "flash",
    [string]$Cwd,
    [string]$Effort,
    [int]$TimeoutMin = 5
)

$ErrorActionPreference = "Stop"

# Resolve the binary (PATH may not have refreshed in this shell)
$agy = Get-Command agy -ErrorAction SilentlyContinue
$agyExe = if ($agy) { $agy.Source } else { Join-Path $env:LOCALAPPDATA "agy\bin\agy.exe" }
if (-not (Test-Path $agyExe)) { Write-Error "agy not found. Install: https://antigravity.google/docs/cli/install"; exit 1 }

if ($PromptFile) { $Prompt = Get-Content $PromptFile -Raw }
if (-not $Prompt) { Write-Error "No prompt given (-Prompt or -PromptFile)"; exit 1 }

# Model shorthands (verified against `agy models` 2026-08-10). Full ids pass through.
$triDir = Join-Path $env:USERPROFILE ".claude\tri-model"
New-Item -ItemType Directory -Force $triDir | Out-Null
$resolved = switch ($Model) {
    "flash" { "gemini-3.6-flash-medium" }
    "pro"   { "gemini-3.1-pro-high" }
    default { $Model }
}

$agyArgs = @("--print", $Prompt, "--model", $resolved, "--output-format", "text", "--print-timeout", "$($TimeoutMin)m")
if ($Effort) { $agyArgs += @("--effort", $Effort) }
if ($Cwd)    { $agyArgs += @("--add-dir", $Cwd) }

$t0 = Get-Date
$prevCwd = Get-Location
try {
    if ($Cwd) { Set-Location $Cwd }
    # Native stderr must not become a terminating error (agy logs to stderr)
    $ErrorActionPreference = "Continue"
    $output = & $agyExe @agyArgs 2>&1 | ForEach-Object { "$_" } | Out-String
    $code = $LASTEXITCODE
    $ErrorActionPreference = "Stop"
} finally { Set-Location $prevCwd }
$secs = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)

# Usage log — evidence for the AI Pro vs Ultra decision
$entry = [ordered]@{
    ts           = (Get-Date -Format o)
    model        = $resolved
    prompt_chars = $Prompt.Length
    output_chars = $output.Length
    seconds      = $secs
    exit         = $code
    cwd          = "$Cwd"
} | ConvertTo-Json -Compress
Add-Content -Path (Join-Path $triDir "agy-usage.jsonl") -Value $entry

Write-Output $output
exit $code
