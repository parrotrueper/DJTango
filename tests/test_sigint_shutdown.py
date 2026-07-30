import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

import pytest


def is_qt_available():
    try:
        import PySide6.QtCore  # noqa: F401
        return True
    except Exception:
        pass
    try:
        import PyQt5.QtCore  # noqa: F401
        return True
    except Exception:
        return False


def test_ttvttm_handles_sigint_and_exits_cleanly(tmp_path):
    if not is_qt_available():
        pytest.skip("Qt bindings not available")

    project_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["TTVTTM_DISABLE_DIR_SCAN"] = "1"
    env["DJ_HOME_PATH"] = str(tmp_path)
    env["PYTHONPATH"] = str(project_root)

    proc = subprocess.Popen(
        [sys.executable, "-m", "ttvttm"],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def send_sigint():
        try:
            proc.send_signal(signal.SIGINT)
        except OSError:
            pass

    timer = threading.Timer(2.0, send_sigint)
    timer.daemon = True
    timer.start()

    try:
        stdout, stderr = proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        pytest.fail("ttvttm did not exit after SIGINT within 15 seconds")

    assert "Starting ttvttm..." in stdout + stderr
    assert proc.returncode == 0, f"Expected clean exit, got {proc.returncode}\nstdout={stdout}\nstderr={stderr}"


def _find_run_ttvttm_sh():
    project_root = Path(__file__).resolve().parents[1]
    run_ttvttm = project_root / "run-ttvttm.sh"
    if run_ttvttm.exists() and run_ttvttm.is_file():
        return run_ttvttm
    return None


def _venv_python_available():
    project_root = Path(__file__).resolve().parents[1]
    python_exec = project_root / ".venv/bin/python"
    if not python_exec.exists():
        return False
    try:
        subprocess.run([str(python_exec), "--version"], capture_output=True, check=True, timeout=10)
        return True
    except Exception:
        return False


def test_quick_main_handles_sigint_and_exits_cleanly(tmp_path):
    if not is_qt_available():
        pytest.skip("Qt bindings not available")

    project_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["TTVTTM_DISABLE_DIR_SCAN"] = "1"
    env["DJ_HOME_PATH"] = str(tmp_path)
    env["PYTHONPATH"] = str(project_root)

    proc = subprocess.Popen(
        [sys.executable, "-m", "ttvttm.quick_main"],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def send_sigint():
        try:
            proc.send_signal(signal.SIGINT)
        except OSError:
            pass

    timer = threading.Timer(2.0, send_sigint)
    timer.daemon = True
    timer.start()

    try:
        stdout, stderr = proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        pytest.fail("ttvttm Quick Main did not exit after SIGINT within 15 seconds")

    assert proc.returncode == 0, (
        f"Expected clean exit from quick_main after SIGINT, got {proc.returncode}\n"
        f"stdout={stdout}\nstderr={stderr}"
    )


def test_run_ttvttm_sh_exits_cleanly_on_sigint(tmp_path):
    run_ttvttm = _find_run_ttvttm_sh()
    if run_ttvttm is None:
        pytest.skip("run-ttvttm.sh not available")
    if not _venv_python_available():
        pytest.skip(".venv Python not available for integration test")

    project_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["TTVTTM_DISABLE_DIR_SCAN"] = "1"
    env["DJ_HOME_PATH"] = str(tmp_path)

    proc = subprocess.Popen(
        [str(run_ttvttm)],
        cwd=project_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def send_sigint():
        try:
            proc.send_signal(signal.SIGINT)
        except OSError:
            pass

    timer = threading.Timer(2.0, send_sigint)
    timer.daemon = True
    timer.start()

    try:
        stdout, stderr = proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        pytest.fail("run-ttvttm.sh did not exit after SIGINT within 15 seconds")

    output = stdout + stderr
    assert proc.returncode == 0, (
        f"Expected clean exit from run-ttvttm.sh after SIGINT, got {proc.returncode}\n"
        f"stdout={stdout}\nstderr={stderr}"
    )
    assert "QQmlApplicationEngine failed" not in output
    assert "ReferenceError" not in output
