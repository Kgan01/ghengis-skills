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

# Two argv hazards on Windows: the ~32K CreateProcess ceiling ("filename or
# extension is too long"), and PowerShell 5.1 mangling embedded quotes and
# newlines in native args (the prompt silently truncates at the first bad
# char - observed as Gemini judging ~10-line fragments of long documents).
# agy's print mode READS workspace files, so anything that is not a short
# clean one-liner goes via file + bootstrap instead of argv.
if ($Prompt.Length -gt 4000 -or $Prompt -match '["\r\n]') {
    $promptDir = Join-Path $triDir "prompts"
    New-Item -ItemType Directory -Force $promptDir | Out-Null
    $promptPath = Join-Path $promptDir ("prompt-{0}.md" -f (Get-Date -Format "yyyyMMdd-HHmmss-fff"))
    Set-Content -Path $promptPath -Value $Prompt -Encoding utf8 -NoNewline
    $sendPrompt = "Read the file $promptPath in your workspace. It contains your complete task and all material. Follow it exactly and reply with the output it asks for - nothing else."
    $extraDir = $promptDir
} else {
    $sendPrompt = $Prompt
    $extraDir = $null
}

$agyArgs = @("--print", $sendPrompt, "--model", $resolved, "--output-format", "text", "--print-timeout", "$($TimeoutMin)m")
if ($Effort)   { $agyArgs += @("--effort", $Effort) }
if ($Cwd)      { $agyArgs += @("--add-dir", $Cwd) }
if ($extraDir) { $agyArgs += @("--add-dir", $extraDir) }

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
    via_file     = [bool]$extraDir
    output_head  = $output.Substring(0, [Math]::Min(160, $output.Length)).Trim()
} | ConvertTo-Json -Compress
Add-Content -Path (Join-Path $triDir "agy-usage.jsonl") -Value $entry

Write-Output $output
exit $code
