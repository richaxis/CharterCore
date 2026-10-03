"""Test-runtime compatibility helpers.

genlayer-test 0.29.x keeps the Direct Mode message tempfile open on Windows
when it attempts to unlink it.  The file is harmless and is released when the
test process restores stdin; ignoring only this specific unlink failure keeps
the repository tests runnable without changing contract behavior.
"""

import os
import sys
import inspect


if sys.platform == "win32":
    try:
        _unlink = os.unlink

        def _unlink_open_tempfile(path, *args, **kwargs):
            try:
                return _unlink(path, *args, **kwargs)
            except PermissionError:
                # genlayer-test 0.29.x unlinks its Direct Mode stdin tempfile
                # while the duplicated stdin handle is still open on Windows.
                # Re-raise every other permission failure.
                caller_files = [frame.filename.replace("\\", "/") for frame in inspect.stack()]
                if any(file.endswith("/gltest/direct/loader.py") for file in caller_files):
                    return None
                raise

        os.unlink = _unlink_open_tempfile
    except ImportError:
        pass
