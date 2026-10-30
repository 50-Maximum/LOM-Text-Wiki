# -*- coding: utf-8 -*-
"""改用 powershell Wait-Process 等待退出，替换会卡死的 tasklist 循环。"""
import io, sys, py_compile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\LegendOfMortal Wiki\src\updater.py"
s = open(P, encoding="utf-8").read()

start = s.index("def _bat_apply(")
end = s.index("def exe_name(")
new = '''def _bat_apply(zip_path, exe_name):
    """解压到临时目录，写批处理：等本进程退出→覆盖→重启。批处理纯 ASCII，路径走环境变量。"""
    stage = os.path.join(tempfile.gettempdir(), "lom_stage_%d" % int(time.time()))
    if os.path.isdir(stage):
        shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(stage)

    log = os.path.join(tempfile.gettempdir(), "lom_update.log")
    bat = os.path.join(tempfile.gettempdir(), "lom_update_%d.bat" % int(time.time()))
    lines = [
        "@echo off",
        "setlocal",
        'echo [start] %DATE% %TIME% >> "%LOM_LOG%"',
        'if not "%LOM_PID%"=="" powershell -NoProfile -WindowStyle Hidden '
        '-Command "Wait-Process -Id %LOM_PID% -ErrorAction SilentlyContinue"',
        "timeout /t 2 /nobreak >nul",
        'echo [copy] %LOM_STAGE% -^> %LOM_ROOT% >> "%LOM_LOG%"',
        'robocopy "%LOM_STAGE%" "%LOM_ROOT%" /E /IS /IT /R:2 /W:1 >> "%LOM_LOG%" 2>&1',
        'if errorlevel 8 xcopy /y /e /i "%LOM_STAGE%\\\\*" "%LOM_ROOT%\\\\" >> "%LOM_LOG%" 2>&1',
        'echo [restart] %LOM_EXE% >> "%LOM_LOG%"',
        'start "" "%LOM_ROOT%\\\\%LOM_EXE%"',
        'rd /s /q "%LOM_STAGE%"',
        'del "%~f0"',
    ]
    with open(bat, "w", encoding="ascii", errors="replace", newline="\\n") as f:
        f.write("\\n".join(lines))
    env = os.environ.copy()
    env.update({"LOM_ROOT": ROOT, "LOM_STAGE": stage,
                "LOM_EXE": exe_name, "LOM_LOG": log, "LOM_PID": str(os.getpid())})
    subprocess.Popen(["cmd", "/c", bat], cwd=tempfile.gettempdir(), env=env,
                     creationflags=0x00000008 | 0x00000200)  # DETACHED | NO_WINDOW
    return bat


'''
s = s[:start] + new + s[end:]
open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("_bat_apply 已改为 Wait-Process，syntax ok")
