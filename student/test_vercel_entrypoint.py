import sys
from pathlib import Path


def test_vercel_entrypoint_exports_application():
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "student"))

    import api.index as vercel_index

    assert callable(getattr(vercel_index, "app", None)) or callable(getattr(vercel_index, "application", None))
