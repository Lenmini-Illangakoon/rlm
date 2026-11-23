# Newly authored archival runner. It was not used for the original executions.
# Pending separate execution/verification. Recovered probe files are not refactored here.
[CmdletBinding()]
param(
    [ValidateSet('all', 'cp4', 'cp2', 'delivery_identity_accounting', 'accounting_extra')]
    [string] $Probe = 'all'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$baseline = 'e11f1a8f8ee4490686e16dd6463233abe08a07eb'
$expectedBranch = 'research/m2-runtime-feasibility'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
$manifestPath = Join-Path $PSScriptRoot 'evidence-manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw 'Expected existing .venv\Scripts\python.exe. This runner installs nothing.'
}
$branch = & git -c "safe.directory=$repoRoot" -C $repoRoot branch --show-current
if ($LASTEXITCODE -ne 0 -or $branch -ne $expectedBranch) {
    throw 'Expected M2 research branch. No branch operation will be performed.'
}
& git -c "safe.directory=$repoRoot" -C $repoRoot cat-file -e "$baseline^{commit}"
if ($LASTEXITCODE -ne 0) { throw 'Pinned baseline commit is unavailable.' }
& git -c "safe.directory=$repoRoot" -C $repoRoot diff --quiet $baseline -- rlm tests pyproject.toml uv.lock
if ($LASTEXITCODE -ne 0) { throw 'Protected upstream files differ from baseline.' }

# Hashes are archive-time checks, not claims about original execution-time hashes.
foreach ($artifact in $manifest.artifacts) {
    $artifactPath = Join-Path $PSScriptRoot $artifact.path
    $digest = (Get-FileHash -LiteralPath $artifactPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($digest -ne $artifact.sha256) { throw "Archive hash mismatch: $($artifact.path)" }
}
foreach ($source in $manifest.protected_source_files) {
    $sourcePath = Join-Path $repoRoot $source.path
    $digest = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($digest -ne $source.archive_time_working_sha256) {
        throw "Protected source hash mismatch: $($source.path)"
    }
}

# This bootstrap is new runner code. It executes each unchanged saved script in
# a fresh isolated Python process only when this runner is invoked.
$bootstrap = @'
import hashlib
import json
import os
import pathlib
import sys

if sys.flags.optimize != 0:
    raise SystemExit("Assertions must be enabled")
repo = pathlib.Path(sys.argv[1]).resolve()
script = pathlib.Path(sys.argv[2]).resolve()
expected_hash = sys.argv[3]
probe_dir = (repo / "research" / "rootcheck" / "m2" / "probes").resolve()
if script.parent != probe_dir:
    raise SystemExit("Unexpected probe path")
payload = script.read_bytes()
if hashlib.sha256(payload).hexdigest() != expected_hash:
    raise SystemExit("Probe hash mismatch")

os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
sys.dont_write_bytecode = True
sys.path.insert(0, str(repo))
violations = []

def deny(reason):
    violations.append(reason)
    raise RuntimeError("Offline reproduction guard: " + reason)

def loopback(host):
    return host in ("127.0.0.1", "::1", b"127.0.0.1", b"::1")

def audit(event, args):
    if event in ("socket.connect", "socket.bind"):
        address = args[1]
        if not isinstance(address, tuple) or not loopback(address[0]):
            deny("non-loopback socket operation")
    elif event == "socket.getaddrinfo":
        if not loopback(args[0]):
            deny("non-loopback name resolution")
    elif event == "socket.sendto":
        deny("datagram networking")
    elif event == "subprocess.Popen" or event == "os.system":
        deny("child process launch")
    elif event.startswith(("os.exec", "os.spawn", "os.posix_spawn")):
        deny("child process launch")
    elif event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        name = os.path.basename(os.fsdecode(args[0])).lower()
        if name.startswith(".env"):
            deny("dotenv file access")

sys.addaudithook(audit)

# Disable dotenv's public entry point too, before importing RLM.
import dotenv
dotenv.load_dotenv = lambda *args, **kwargs: False

import rlm.clients as clients
import rlm.core.rlm as core

def no_real_client(*args, **kwargs):
    deny("unmocked LM client creation")

# Each original probe temporarily patches core.get_client to its own MockLM
# or MockLM subclass. Any accidental unpatched path fails closed.
clients.get_client = no_real_client
core.get_client = no_real_client

print("M2_ARCHIVE_REPRO_ENV " + json.dumps({
    "python": sys.version,
    "platform": sys.platform,
    "assertions_enabled": sys.flags.optimize == 0,
    "dotenv_disabled": True,
    "guard": "mock factory required; numeric loopback only; no child processes",
    "script_sha256": expected_hash,
}, sort_keys=True), flush=True)

namespace = {"__name__": "__main__", "__file__": str(script)}
exec(compile(payload, str(script), "exec"), namespace)
if violations:
    raise SystemExit("Offline guard observed blocked operations")
'@

$selectedRuns = @($manifest.probe_runs | Where-Object { $Probe -eq 'all' -or $_.run_id -eq $Probe })
if ($selectedRuns.Count -eq 0) { throw 'No probe selected.' }
$envNames = @('PYTHON_DOTENV_DISABLED', 'PYTHONDONTWRITEBYTECODE', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD')
$previous = @{}
foreach ($name in $envNames) {
    $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
    [Environment]::SetEnvironmentVariable($name, '1', 'Process')
}
$invocationId = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ') + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
$outputDir = Join-Path $PSScriptRoot "test-results\local\$invocationId"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$lineFeed = [string][char]10
Push-Location -LiteralPath $repoRoot
try {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    foreach ($run in $selectedRuns) {
        $scriptPath = Join-Path $PSScriptRoot $run.script
        $artifact = @($manifest.artifacts | Where-Object { $_.path -eq $run.script })
        if ($artifact.Count -ne 1) { throw 'Expected exactly one probe hash.' }
        $started = [DateTime]::UtcNow.ToString('o')
        # Keep native stderr as captured evidence even on Windows PowerShell,
        # where ErrorActionPreference=Stop could otherwise abort before logging.
        $nativeErrorPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = 'Continue'
            $rawOutput = @($bootstrap | & $python -I -B - $repoRoot $scriptPath $artifact[0].sha256 2>&1)
            $exitCode = $LASTEXITCODE
        }
        finally { $ErrorActionPreference = $nativeErrorPreference }
        $lines = @($rawOutput | ForEach-Object { $_.ToString() })
        $rows = @($lines | Where-Object { $_.StartsWith('{') } | ForEach-Object { $_ | ConvertFrom-Json })
        $actualIds = @($rows | ForEach-Object { $_.probe })
        $expectedIds = @($run.original_case_identifiers)
        $idsMatch = ($actualIds.Count -eq $expectedIds.Count) -and
            (($actualIds -join $lineFeed) -ceq ($expectedIds -join $lineFeed))
        $allPass = @($rows | Where-Object { $_.status -ne 'PASS' }).Count -eq 0
        $verified = $exitCode -eq 0 -and $idsMatch -and $allPass
        $record = [ordered]@{
            record_kind = 'later saved-script reproduction; never original evidence'
            invocation_id = $invocationId
            started_utc = $started
            completed_utc = [DateTime]::UtcNow.ToString('o')
            baseline = $baseline
            probe_run = $run.run_id
            script_sha256 = $artifact[0].sha256
            exit_code = $exitCode
            verified_by_runner = $verified
            case_count = $rows.Count
            output_lines = $lines
        }
        $recordPath = Join-Path $outputDir ($run.run_id + '.json')
        [System.IO.File]::WriteAllText($recordPath, ($record | ConvertTo-Json -Depth 30) + $lineFeed, $utf8)
        $lines | ForEach-Object { Write-Output $_ }
        if (-not $verified) { throw "Probe failed verification; local record: $recordPath" }
        Write-Output "Saved-script assertions verified: $($run.run_id); $($rows.Count) original cases"
    }
    Write-Output "Local reproduction records: $outputDir"
}
finally {
    Pop-Location
    foreach ($name in $envNames) {
        [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process')
    }
}
