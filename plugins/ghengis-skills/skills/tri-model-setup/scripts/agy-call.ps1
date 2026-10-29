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

# Model shorthands resolve against the LIVE `agy models` list (cached 12h), so a
# new Gemini release needs no edit here. flash[-low|-high] = newest gemini-*-flash
# (medium by default); pro[-low|-medium] = newest non-flash Gemini (high by default,
# e.g. gemini-4-argon-high). Full ids pass through untouched.
$triDir = Join-Path $env:USERPROFILE ".claude\tri-model"
New-Item -ItemType Directory -Force $triDir | Out-Null

function Get-AgyModelIds {
    $cache = Join-Path $triDir "agy-models.txt"
    $fresh = (Test-Path $cache) -and ((Get-Date) - (Get-Item $cache).LastWriteTime).TotalHours -lt 12
    if (-not $fresh) {
        $ErrorActionPreference = "Continue"
        $list = & $agyExe models 2>$null | Where-Object { $_ -match '^\S+\t' }
        $ErrorActionPreference = "Stop"
        if ($list) { Set-Content -Path $cache -Value $list -Encoding ascii }
    }
    if (Test-Path $cache) { Get-Content $cache | ForEach-Object { ($_ -split "`t")[0] } }
}

function Resolve-GeminiAlias([string]$alias) {
    if ($alias -notmatch '^(flash|pro)(-(low|medium|high))?$') { return $alias }
    $family = $Matches[1]
    $tier = if ($Matches[3]) { $Matches[3] } elseif ($family -eq "flash") { "medium" } else { "high" }
    $best = $null; $bestVer = $null
    foreach ($id in (Get-AgyModelIds)) {
        if ($id -notmatch '^gemini-(\d+(\.\d+)?)-(.+)-(low|medium|high)$') { continue }
        if ($Matches[4] -ne $tier) { continue }
        $isFlash = $Matches[3] -eq "flash"
        if (($family -eq "flash") -ne $isFlash) { continue }
        $v = $Matches[1]; if ($v -notmatch '\.') { $v = "$v.0" }
        $ver = [version]$v
        if (-not $best -or $ver -gt $bestVer) { $best = $id; $bestVer = $ver }
    }
    if ($best) { return $best }
    # agy unreachable and no cache: last ids seen live (2026-10-29)
    if ($family -eq "flash") { return "gemini-3.8-flash-$tier" } else { return "gemini-4-argon-$tier" }
}

$resolved = Resolve-GeminiAlias $Model

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
