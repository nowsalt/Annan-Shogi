"""テストランナー (標準ライブラリのみで実行可能)."""
import sys
import traceback

from tests.test_core import *
from tests.test_annan_rule import *
from tests.test_legal_moves import *


if __name__ == "__main__":
    # test_ で始まる関数を全て実行
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = failed = 0
    for t in tests:
        try:
            t()
            sys.stdout.write(f"  PASS: {t.__name__}\n")
            sys.stdout.flush()
            passed += 1
        except Exception as e:
            sys.stdout.write(f"  FAIL: {t.__name__}: {e}\n")
            sys.stdout.flush()
            traceback.print_exc()
            failed += 1
    sys.stdout.write(f"\n{passed} passed, {failed} failed\n")
    sys.stdout.flush()
    sys.exit(failed)
