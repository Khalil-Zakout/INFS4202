# Create all the issue labels once (run by one person, e.g. Khalil). Needs: gh auth login.
# Usage:  .\scripts\create_labels.ps1
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
$repo = if ($env:REPO) { $env:REPO } else { gh repo view --json nameWithOwner -q .nameWithOwner }
Write-Host "Creating labels in $repo"
gh label create "severity:critical" --color "b60205" --description "Blocks a core function, loses or exposes data, or breaks security" --force --repo $repo
gh label create "severity:major" --color "d93f0b" --description "A requirement is violated with a significant effect" --force --repo $repo
gh label create "severity:minor" --color "fbca04" --description "A requirement is violated with a small effect" --force --repo $repo
gh label create "severity:enhancement" --color "c2e0c6" --description "No requirement violated, but a concrete change would clearly improve an existing function" --force --repo $repo
gh label create "priority:p1" --color "5319e7" --description "Fix first" --force --repo $repo
gh label create "priority:p2" --color "8a63d2" --description "Fix soon" --force --repo $repo
gh label create "priority:p3" --color "c5b3f0" --description "Fix when possible" --force --repo $repo
gh label create "functional" --color "1d76db" --description "Functional requirement or business rule" --force --repo $repo
gh label create "integration" --color "0e8a16" --description "Portal and Engine, or Portal and external services" --force --repo $repo
gh label create "state" --color "006b75" --description "State transitions, sequences, concurrency" --force --repo $repo
gh label create "performance" --color "e99695" --description "Response time, throughput, volume, endurance" --force --repo $repo
gh label create "security" --color "b60205" --description "Access control, injection, sessions, secrets" --force --repo $repo
gh label create "ai" --color "f9d0c4" --description "AI Assistant behaviour and prompts" --force --repo $repo
gh label create "ui" --color "bfdadc" --description "Usability, accessibility, compatibility" --force --repo $repo
gh label create "configuration" --color "d4c5f9" --description "Settings and configuration" --force --repo $repo
gh label create "requirements" --color "fef2c0" --description "Defect in the specification itself" --force --repo $repo
gh label create "tests" --color "c2e0c6" --description "Defect in the shipped test suite" --force --repo $repo
gh label create "duplicate" --color "cfd3d7" --description "Same defect as another issue" --force --repo $repo
gh label create "invalid" --color "e4e669" --description "Not reproducible, or no requirement violated and not an enhancement" --force --repo $repo
