from unittest.mock import MagicMock, patch

import pytest


def test_build_falls_back_to_vitis_hls(tmp_path):
    """vitis_hls used when vitis-run absent (issue #1463). Fails on main, passes on branch."""
    from hls4ml.backends.vitis.vitis_backend import VitisBackend

    model = MagicMock()
    model.config.get_output_dir.return_value = str(tmp_path)
    model.config.get_project_name.return_value = 'test'

    captured = {}

    def fake_popen(cmd, **kwargs):
        captured['cmd'] = cmd
        proc = MagicMock()
        proc.returncode = 0
        proc.communicate.return_value = (None, None)
        return proc

    with (
        patch('sys.platform', 'linux'),
        patch('shutil.which', side_effect=lambda c: None if c == 'vitis-run' else '/usr/bin/vitis_hls'),
        patch('subprocess.Popen', side_effect=fake_popen),
        patch('hls4ml.backends.vitis.vitis_backend.parse_vivado_report', return_value={}),
    ):
        VitisBackend.__new__(VitisBackend).build(model)

    assert captured['cmd'] == 'vitis_hls -f build_prj.tcl'


def test_build_raises_when_neither_found(tmp_path):
    """Exception raised when neither vitis-run nor vitis_hls is on PATH."""
    from hls4ml.backends.vitis.vitis_backend import VitisBackend

    model = MagicMock()
    model.config.get_output_dir.return_value = str(tmp_path)

    with patch('sys.platform', 'linux'), patch('shutil.which', return_value=None):
        with pytest.raises(Exception, match='vitis_hls'):
            VitisBackend.__new__(VitisBackend).build(model)
