# sync_check.ps1 — is the deployed tri-model harness still identical to the
# ghengis-skills copy that ships it? Run after deploying to a new machine, and
# after editing anything locally (so the change gets carried back).
#
#   powershell -File ~/.claude/tri-model/sync_check.ps1          # report drift
#   powershell -File ~/.claude/tri-model/sync_check.ps1 -Push    # copy local -> skill
#   powershell -File ~/.claude/tri-model/sync_check.ps1 -Pull    # copy skill -> local
#
# Windows PowerShell 5.1 compatible - no ternary, no null-coalescing. pwsh is NOT
# assumed present (it is absent on a stock Windows 11 box).
param([switch]$Push, [switch]$Pull)

$g = Join-Path $env:USERPROFILE ".claude"

# The marketplace directory is named after however the plugin was added - "Kgan01"
# when installed from the GitHub owner, "ghengis-skills-marketplace" when added by
# reload-ghengis. Never hardcode either, and never just take the first directory
# found: a stale orphan clone left by an earlier reload can sort ahead of the real
# one alphabetically and silently diff you against a dead copy (observed 2026-08-12).
# installed_plugins.json is authoritative about which marketplace is actually live.
$mkRoot = Join-Path $g "plugins\marketplaces"
$skill = $null
$rel = "plugins\ghengis-skills\skills\tri-model-setup"

$installed = Join-Path $g "plugins\installed_plugins.json"
if (Test-Path $installed) {
    try {
        $j = Get-Content $installed -Raw | ConvertFrom-Json
        foreach ($k in $j.plugins.PSObject.Properties.Name) {
            if ($k -like "ghengis-skills@*") {
                $mkName = $k.Split("@")[1]
                $cand = Join-Path (Join-Path $mkRoot $mkName) $rel
                if (Test-Path $cand) { $skill = $cand; break }
            }
        }
    } catch { }   # fall through to the scan
}

if (-not $skill -and (Test-Path $mkRoot)) {
    foreach ($mk in Get-ChildItem $mkRoot -Directory -ErrorAction SilentlyContinue) {
        $cand = Join-Path $mk.FullName $rel
        if (Test-Path $cand) { $skill = $cand; break }
    }
}
if (-not $skill) {
    Write-Error "tri-model-setup skill not found under any marketplace in $mkRoot"
    exit 1
}
Write-Host "skill source: $skill" -ForegroundColor DarkGray

# local path -> skill path
$map = [ordered]@{
    "$g\scripts\agy-call.ps1"           = "$skill\scripts\agy-call.ps1"
    "$g\tri-model\dashboard.py"         = "$skill\scripts\dashboard.py"
    "$g\tri-model\model_advisor.py"     = "$skill\scripts\model_advisor.py"
    "$g\tri-model\sync_check.ps1"       = "$skill\scripts\sync_check.ps1"
    "$g\agents\gemini.md"               = "$skill\assets\gemini-agent.md"
    "$g\commands\gemini.md"             = "$skill\assets\commands\gemini.md"
    "$g\commands\opinion.md"            = "$skill\assets\commands\opinion.md"
    "$g\commands\fusion.md"             = "$skill\assets\commands\fusion.md"
    "$g\commands\auto-validate.md"      = "$skill\assets\commands\auto-validate.md"
    "$g\commands\adw.md"                = "$skill\assets\commands\adw.md"
    "$g\commands\gauntlet.md"           = "$skill\assets\commands\gauntlet.md"
    "$g\tri-model\adw\rosters.yaml"     = "$skill\assets\adw\rosters.yaml"
}
foreach ($w in Get-ChildItem "$skill\assets\adw\workflows" -Filter *.yaml -ErrorAction SilentlyContinue) {
    $map["$g\tri-model\adw\workflows\$($w.Name)"] = $w.FullName
}

$drift = 0
foreach ($local in $map.Keys) {
    $remote = $map[$local]
    $lh = $null; if (Test-Path $local)  { $lh = (Get-FileHash $local).Hash }
    $rh = $null; if (Test-Path $remote) { $rh = (Get-FileHash $remote).Hash }
    $name = Split-Path $local -Leaf
    if (-not $lh -and -not $rh) { continue }
    if (-not $lh)      { Write-Host "MISSING LOCALLY : $name" -ForegroundColor Yellow; $drift++ }
    elseif (-not $rh)  { Write-Host "MISSING IN SKILL: $name" -ForegroundColor Yellow; $drift++ }
    elseif ($lh -ne $rh) { Write-Host "DRIFT           : $name" -ForegroundColor Red; $drift++ }
    if ($Push -and $lh) { New-Item -ItemType Directory -Force (Split-Path $remote) | Out-Null; Copy-Item $local $remote -Force }
    if ($Pull -and $rh) { New-Item -ItemType Directory -Force (Split-Path $local)  | Out-Null; Copy-Item $remote $local -Force }
}

if ($Push) { Write-Host "pushed local -> skill (commit the skill repo to publish)" -ForegroundColor Green }
elseif ($Pull) { Write-Host "pulled skill -> local" -ForegroundColor Green }
elseif ($drift -eq 0) { Write-Host "in sync: $($map.Count) files identical" -ForegroundColor Green }
else { Write-Host "`n$drift file(s) differ - run with -Push (local is newer) or -Pull (skill is newer)" -ForegroundColor Yellow }
exit 0
