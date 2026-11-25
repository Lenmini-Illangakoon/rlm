"""Windows AppContainer launcher. No credential APIs or automatic elevation.

Only new staging paths receive ACL entries. Research and runtime source ACLs are
never changed. A failure to create the restricted process is a hard failure.
"""

import ctypes as C
import json
import shutil
import subprocess
import sys
import time
import uuid
import zipfile
from ctypes import wintypes as W
from pathlib import Path

from ..common import REPO, WORKSPACE, preserved_hashes, sha, write_json

K = C.WinDLL("kernel32", use_last_error=True)
A = C.WinDLL("advapi32", use_last_error=True)
U = C.WinDLL("userenv", use_last_error=True)
P = C.c_void_p
SIZE = C.c_size_t


class SecurityAttributes(C.Structure):
    _fields_ = [("nLength", W.DWORD), ("lpSecurityDescriptor", P), ("bInheritHandle", W.BOOL)]


class Trustee(C.Structure):
    _fields_ = [("pMultipleTrustee", P), ("MultipleTrusteeOperation", C.c_int),
                ("TrusteeForm", C.c_int), ("TrusteeType", C.c_int), ("ptstrName", P)]


class ExplicitAccess(C.Structure):
    _fields_ = [("grfAccessPermissions", W.DWORD), ("grfAccessMode", C.c_int),
                ("grfInheritance", W.DWORD), ("Trustee", Trustee)]


class Startup(C.Structure):
    _fields_ = [("cb", W.DWORD), ("lpReserved", W.LPWSTR), ("lpDesktop", W.LPWSTR),
                ("lpTitle", W.LPWSTR), ("dwX", W.DWORD), ("dwY", W.DWORD),
                ("dwXSize", W.DWORD), ("dwYSize", W.DWORD), ("dwXCountChars", W.DWORD),
                ("dwYCountChars", W.DWORD), ("dwFillAttribute", W.DWORD),
                ("dwFlags", W.DWORD), ("wShowWindow", W.WORD), ("cbReserved2", W.WORD),
                ("lpReserved2", P), ("hStdInput", W.HANDLE), ("hStdOutput", W.HANDLE),
                ("hStdError", W.HANDLE)]


class ProcessInfo(C.Structure):
    _fields_ = [("hProcess", W.HANDLE), ("hThread", W.HANDLE),
                ("dwProcessId", W.DWORD), ("dwThreadId", W.DWORD)]


class StartupEx(C.Structure):
    _fields_ = [("StartupInfo", Startup), ("lpAttributeList", P)]


class SecurityCapabilities(C.Structure):
    _fields_ = [("AppContainerSid", P), ("Capabilities", P),
                ("CapabilityCount", W.DWORD), ("Reserved", W.DWORD)]


class BasicLimits(C.Structure):
    _fields_ = [("PerProcessUserTimeLimit", C.c_longlong), ("PerJobUserTimeLimit", C.c_longlong),
                ("LimitFlags", W.DWORD), ("MinimumWorkingSetSize", SIZE),
                ("MaximumWorkingSetSize", SIZE), ("ActiveProcessLimit", W.DWORD),
                ("Affinity", SIZE), ("PriorityClass", W.DWORD), ("SchedulingClass", W.DWORD)]


class IoCounters(C.Structure):
    _fields_ = [(name, C.c_ulonglong) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class ExtendedLimits(C.Structure):
    _fields_ = [("BasicLimitInformation", BasicLimits), ("IoInfo", IoCounters),
                ("ProcessMemoryLimit", SIZE), ("JobMemoryLimit", SIZE),
                ("PeakProcessMemoryUsed", SIZE), ("PeakJobMemoryUsed", SIZE)]


def bind(dll, name, restype, args):
    function = getattr(dll, name)
    function.restype, function.argtypes = restype, args
    return function


bind(K, "GetCurrentProcess", W.HANDLE, [])
bind(K, "CloseHandle", W.BOOL, [W.HANDLE])
bind(K, "LocalFree", P, [P])
bind(A, "ConvertStringSidToSidW", W.BOOL, [W.LPCWSTR, C.POINTER(P)])
bind(A, "GetNamedSecurityInfoW", W.DWORD, [W.LPCWSTR, C.c_int, W.DWORD, P, P, C.POINTER(P), P, C.POINTER(P)])
bind(A, "SetEntriesInAclW", W.DWORD, [W.ULONG, P, P, C.POINTER(P)])
bind(A, "SetNamedSecurityInfoW", W.DWORD, [W.LPWSTR, C.c_int, W.DWORD, P, P, P, P])
bind(A, "ConvertStringSecurityDescriptorToSecurityDescriptorW", W.BOOL, [W.LPCWSTR, W.DWORD, C.POINTER(P), P])
bind(K, "CreateDirectoryW", W.BOOL, [W.LPCWSTR, C.POINTER(SecurityAttributes)])
bind(K, "CreateJobObjectW", W.HANDLE, [P, W.LPCWSTR])
bind(K, "SetInformationJobObject", W.BOOL, [W.HANDLE, C.c_int, P, W.DWORD])
bind(K, "AssignProcessToJobObject", W.BOOL, [W.HANDLE, W.HANDLE])
bind(K, "ResumeThread", W.DWORD, [W.HANDLE])
bind(K, "WaitForSingleObject", W.DWORD, [W.HANDLE, W.DWORD])
bind(K, "GetExitCodeProcess", W.BOOL, [W.HANDLE, C.POINTER(W.DWORD)])
bind(K, "TerminateProcess", W.BOOL, [W.HANDLE, W.UINT])
bind(U, "DeriveAppContainerSidFromAppContainerName", C.c_long, [W.LPCWSTR, C.POINTER(P)])
bind(U, "CreateAppContainerProfile", C.c_long, [W.LPCWSTR, W.LPCWSTR, W.LPCWSTR, P, W.DWORD, C.POINTER(P)])
bind(U, "DeleteAppContainerProfile", C.c_long, [W.LPCWSTR])
bind(A, "FreeSid", P, [P])
bind(A, "ConvertSidToStringSidW", W.BOOL, [P, C.POINTER(W.LPWSTR)])
bind(K, "InitializeProcThreadAttributeList", W.BOOL, [P, W.DWORD, W.DWORD, C.POINTER(SIZE)])
bind(K, "UpdateProcThreadAttribute", W.BOOL, [P, W.DWORD, SIZE, P, SIZE, P, P])
bind(K, "DeleteProcThreadAttributeList", None, [P])
bind(K, "CreateProcessW", W.BOOL, [W.LPCWSTR, W.LPWSTR, P, P, W.BOOL, W.DWORD,
                                  P, W.LPCWSTR, C.POINTER(StartupEx), C.POINTER(ProcessInfo)])


def appcontainer_sid(name):
    pointer, text = P(), W.LPWSTR()
    error = U.DeriveAppContainerSidFromAppContainerName(name, C.byref(pointer))
    if error < 0:
        raise OSError(f'DeriveAppContainerSidFromAppContainerName HRESULT {error:#x}')
    try:
        check(A.ConvertSidToStringSidW(pointer, C.byref(text)), 'ConvertSidToStringSidW')
        return text.value
    finally:
        if text:
            K.LocalFree(text)
        A.FreeSid(pointer)


def register_profile(stage):
    name = stage.get('profile_name', 'RootCheck.Offline.' + Path(stage['root']).name)
    pointer = P()
    error = U.CreateAppContainerProfile(name, name, 'Offline RLM isolation, zero network capabilities',
                                        None, 0, C.byref(pointer))
    if pointer:
        A.FreeSid(pointer)
    if error < 0 and (error & 0xFFFFFFFF) != 0x800700B7:
        raise OSError(f'CreateAppContainerProfile HRESULT {error & 0xFFFFFFFF:#x}')
    stage['profile_name'] = name
    stage['profile_registered'] = True
    return stage


def check(ok, operation):
    if not ok:
        raise C.WinError(C.get_last_error(), operation)


def sid(text):
    pointer = P()
    check(A.ConvertStringSidToSidW(text, C.byref(pointer)), "ConvertStringSidToSidW")
    return pointer


def grant_stage(path: Path, restriction: str, mask: int, allowed_root=None, revoke=False):
    if not path.resolve().is_relative_to(allowed_root or WORKSPACE / 'isolation-staging'):
        raise ValueError('Refusing ACL change outside staging')
    old_acl, descriptor, new_acl = P(), P(), P()
    principal = sid(restriction)
    try:
        error = A.GetNamedSecurityInfoW(str(path), 1, 4, None, None, C.byref(old_acl), None, C.byref(descriptor))
        if error:
            raise C.WinError(error)
        entry = ExplicitAccess(mask, 4 if revoke else 1, 3, Trustee(None, 0, 0, 0, principal))
        error = A.SetEntriesInAclW(1, C.byref(entry), old_acl, C.byref(new_acl))
        if error:
            raise C.WinError(error)
        error = A.SetNamedSecurityInfoW(str(path), 1, 4, None, None, new_acl, None)
        if error:
            raise C.WinError(error)
    finally:
        for pointer in (principal, descriptor, new_acl):
            if pointer:
                K.LocalFree(pointer)


def low_directory(path: Path):
    if not path.resolve().is_relative_to(WORKSPACE / 'isolation-staging'):
        raise ValueError('Refusing label outside staging')
    descriptor = P()
    check(A.ConvertStringSecurityDescriptorToSecurityDescriptorW('S:(ML;OICI;NW;;;LW)', 1,
                                                                 C.byref(descriptor), None), 'Low directory descriptor')
    try:
        attributes = SecurityAttributes(C.sizeof(SecurityAttributes), descriptor, False)
        check(K.CreateDirectoryW(str(path), C.byref(attributes)), 'CreateDirectoryW(low integrity)')
    finally:
        K.LocalFree(descriptor)


def build_stage():
    preserved_hashes()
    root = WORKSPACE / "isolation-staging" / uuid.uuid4().hex
    payload, work = root / "payload", root / "work"
    payload.mkdir(parents=True)
    low_directory(work)
    for name in ("temp", "profile"):
        (work / name).mkdir()
    restriction = appcontainer_sid('RootCheck.Offline.' + root.name)
    base = Path(sys.base_prefix)
    runtime = payload / "python"
    runtime.mkdir()
    for name in ("python.exe", "python312.dll", "python3.dll", "vcruntime140.dll", "vcruntime140_1.dll"):
        shutil.copyfile(base / name, runtime / name)
    shutil.copytree(base / "DLLs", runtime / "DLLs", ignore=shutil.ignore_patterns("__pycache__"))
    with zipfile.ZipFile(runtime / "python312.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((base / "Lib").rglob("*.py")):
            relative = path.relative_to(base / "Lib")
            if any(p in {"site-packages", "test", "tests", "idlelib", "tkinter", "ensurepip", "__pycache__"} for p in relative.parts):
                continue
            archive.write(path, relative.as_posix())
    site = runtime / "site-packages"
    for package in ("dotenv", "rich", "pygments"):
        shutil.copytree(Path(sys.prefix) / "Lib/site-packages" / package, site / package,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (runtime / "python312._pth").write_text("python312.zip\nDLLs\nsite-packages\n../repo\n", encoding="utf-8")
    staged_repo = payload / "repo"
    for path in (REPO / "rlm").rglob("*.py"):
        target = staged_repo / path.relative_to(REPO)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    # Explicit allowlist: no oracle, evaluator, assessment, result or credential tree.
    for relative in ("__init__.py", "common.py", "fixtures/__init__.py", "fixtures/programs.py",
                     "runners/__init__.py", "runners/mock.py", "runners/observe.py",
                     "runners/offline_guard.py", "runners/config.py", "runners/pilot.json",
                     "runners/isolation_worker.py", "runners/temp_permissions.py", "runners/broker_client.py"):
        target = staged_repo / "experiments/official_baseline_h2_h5_h6" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(WORKSPACE / relative, target)
    # Grant the extra restricting SID only the staged runtime, then writable scratch.
    grant_stage(root, restriction, 0x1200A9)
    grant_stage(work, restriction, 0x1301BF)
    manifest = {"root": str(root), "appcontainer_sid": restriction, 'profile_registered': False,
                "files": {p.relative_to(root).as_posix(): sha(p.read_bytes())
                          for p in payload.rglob('*') if p.is_file()}}
    write_json(root / "stage-manifest.json", manifest)
    return manifest


def verify_stage(stage):
    root = Path(stage['root']).resolve()
    if not root.is_relative_to(WORKSPACE / 'isolation-staging'):
        raise ValueError('Stage outside authorized experiment directory')
    actual = {p.relative_to(root).as_posix() for p in (root / 'payload').rglob('*') if p.is_file()}
    if actual != set(stage['files']):
        raise ValueError('Staged payload inventory changed')
    for relative, expected in stage['files'].items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root / 'payload') or sha(path.read_bytes()) != expected:
            raise ValueError(f'Staged payload changed: {relative}')
    for path in (root / 'payload/repo/rlm').rglob('*.py'):
        original = REPO / path.relative_to(root / 'payload/repo')
        if sha(path.read_bytes()) != sha(original.read_bytes()):
            raise ValueError(f'Pinned staged runtime differs: {path.name}')


def launch(stage, request, timeout=60, poll=None):
    root = Path(stage["root"])
    work, payload = Path(stage.get('work', str(root / 'work'))), root / "payload"
    if not work.resolve().is_relative_to(root.resolve()):
        raise ValueError('Scratch path must stay inside stage')
    (work / 'response.json').unlink(missing_ok=True)
    write_json(work / "request.json", {**request, 'appcontainer_sid': stage.get('appcontainer_sid')})
    executable = payload / "python/python.exe"
    script = payload / "repo/experiments/official_baseline_h2_h5_h6/runners/isolation_worker.py"
    command = C.create_unicode_buffer(subprocess.list2cmdline([str(executable), "-I", "-B", str(script), str(work)]))
    # Construct from literals; never copy the parent environment or inspect API keys.
    environment = {"SystemRoot": "C:\\Windows", "WINDIR": "C:\\Windows",
                   "TEMP": str(work / "temp"), "TMP": str(work / "temp"),
                   "USERPROFILE": str(work / "profile"), "PATH": str(executable.parent),
                   "LOCALAPPDATA": str(work / 'profile/AppData/Local'),
                   "APPDATA": str(work / 'profile/AppData/Roaming')}
    for key in ('LOCALAPPDATA', 'APPDATA'):
        Path(environment[key]).mkdir(parents=True, exist_ok=True)
    env_block = C.create_unicode_buffer("\0".join(f"{k}={v}" for k, v in sorted(environment.items())) + "\0\0")
    app_sid = None
    attributes = None
    job, process = None, ProcessInfo()
    started = time.monotonic()
    try:
        job = K.CreateJobObjectW(None, None)
        check(job, "CreateJobObjectW")
        limits = ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = 0x2000 | 0x8  # kill-on-close, one process
        limits.BasicLimitInformation.ActiveProcessLimit = 1
        check(K.SetInformationJobObject(job, 9, C.byref(limits), C.sizeof(limits)), "SetInformationJobObject")
        ui = W.DWORD(0xFF)
        check(K.SetInformationJobObject(job, 4, C.byref(ui), C.sizeof(ui)), "Job UI restrictions")
        if stage.get('appcontainer_sid') and stage.get('profile_registered'):
            app_sid = sid(stage['appcontainer_sid'])
            capabilities = SecurityCapabilities(app_sid, None, 0, 0)
            size = SIZE()
            K.InitializeProcThreadAttributeList(None, 1, 0, C.byref(size))
            attributes = C.create_string_buffer(size.value)
            check(K.InitializeProcThreadAttributeList(attributes, 1, 0, C.byref(size)), 'InitializeProcThreadAttributeList')
            check(K.UpdateProcThreadAttribute(attributes, 0, 0x20009, C.byref(capabilities),
                                              C.sizeof(capabilities), None, None), 'Security capabilities')
            startup_ex = StartupEx()
            startup_ex.StartupInfo.cb = C.sizeof(startup_ex)
            startup_ex.lpAttributeList = C.cast(attributes, P)
            check(K.CreateProcessW(str(executable), command, None, None, False,
                                   0x08000000 | 0x400 | 4 | 0x80000, env_block, str(work),
                                   C.byref(startup_ex), C.byref(process)), 'CreateProcessW(AppContainer)')
        else:
            raise RuntimeError('Registered AppContainer required; no unrestricted fallback')
        check(K.AssignProcessToJobObject(job, process.hProcess), "AssignProcessToJobObject")
        if K.ResumeThread(process.hThread) == 0xFFFFFFFF:
            check(False, "ResumeThread")
        while True:
            if poll:
                poll()
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("Restricted worker exceeded external deadline")
            wait = K.WaitForSingleObject(process.hProcess, min(20, max(1, int(remaining * 1000))))
            if wait != 258:
                break
        check(wait == 0, "WaitForSingleObject")
        code = W.DWORD()
        check(K.GetExitCodeProcess(process.hProcess, C.byref(code)), "GetExitCodeProcess")
        output = work / "response.json"
        return {"exit_code": code.value, "elapsed_seconds": time.monotonic() - started,
                "response": strict_json(read_worker_file(output, 64 * 1024 * 1024)) if output.exists() else None,
                "boundary": "appcontainer-job", "stage_root": str(root)}
    finally:
        if process.hProcess:
            K.TerminateProcess(process.hProcess, 125)
            check(K.WaitForSingleObject(process.hProcess, 5000) == 0, 'Wait for worker exit')
        for handle in (process.hThread, process.hProcess, job):
            if handle:
                K.CloseHandle(handle)
        if attributes:
            K.DeleteProcThreadAttributeList(attributes)
        if app_sid:
            K.LocalFree(app_sid)


def reject_json_constant(value):
    raise ValueError('Non-finite JSON number: ' + value)


def strict_json(data):
    return json.loads(data, parse_constant=reject_json_constant)


def read_worker_file(path: Path, maximum: int) -> bytes:
    """Read a bounded regular file handle; never follow a worker-created reparse leaf."""
    create = bind(K, 'CreateFileW', W.HANDLE, [W.LPCWSTR, W.DWORD, W.DWORD, P, W.DWORD, W.DWORD, W.HANDLE])
    info = bind(K, 'GetFileInformationByHandleEx', W.BOOL, [W.HANDLE, C.c_int, P, W.DWORD])
    size_fn = bind(K, 'GetFileSizeEx', W.BOOL, [W.HANDLE, C.POINTER(C.c_longlong)])
    read = bind(K, 'ReadFile', W.BOOL, [W.HANDLE, P, W.DWORD, C.POINTER(W.DWORD), P])
    # Share delete permits the atomic rename that publishes a request; writes
    # remain excluded, and this handle continues to reference the same file.
    handle = create(str(path), 0x80000000, 5, None, 3, 0x00200000, None)
    check(handle != P(-1).value, 'Open worker file without following reparse points')
    try:
        attributes = (W.DWORD * 2)()
        check(info(handle, 9, attributes, C.sizeof(attributes)), 'Worker file attributes')
        if attributes[0] & (0x400 | 0x10):
            raise ValueError('Worker output must be a regular file')
        size = C.c_longlong()
        check(size_fn(handle, C.byref(size)), 'Worker file size')
        if not 0 <= size.value <= maximum:
            raise ValueError('Worker file exceeds transport limit')
        buffer, count = C.create_string_buffer(size.value), W.DWORD()
        check(read(handle, buffer, size.value, C.byref(count), None), 'Read worker file')
        if count.value != size.value:
            raise ValueError('Incomplete worker file')
        return buffer.raw
    finally:
        K.CloseHandle(handle)
