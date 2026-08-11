# sync_check.ps1 — is the deployed tri-model harness still identical to the
# ghengis-skills copy that ships it? Run after deploying to a new machine, and
# after editing anything locally (so the change gets carried back).
#
#   pwsh ~/.claude/tri-model/sync_check.ps1          # report drift
#   pwsh ~/.claude/tri-model/sync_check.ps1 -Push    # copy local -> skill
#   pwsh ~/.claude/tri-model/sync_check.ps1 -Pull    # copy skill -> local
param([switch]$Push, [switch]$Pull)

$g = Join-Path $env:USERPROFILE ".claude"
$skill = Join-Path $g "plugins\marketplaces\ghengis-skills-marketplace\plugins\ghengis-skills\skills\tri-model-setup"
if (-not (Test-Path $skill)) { Write-Error "tri-model-setup skill not found at $skill"; exit 1 }

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
    $lh = (Test-Path $local) ? (Get-FileHash $local).Hash : $null
    $rh = (Test-Path $remote) ? (Get-FileHash $remote).Hash : $null
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
