"""The store only ever grows: a new release is reported as added, a vanished one as removed (which stops the run)."""
import unittest

from build_store import changes


def store(*versions):
    return [{"name": "DeckyEQ", "versions": [{"name": v} for v in versions]}]


class ChangesTest(unittest.TestCase):
    old = {("DeckyEQ", "1.0.0", "url-1"), ("DeckyEQ", "1.1.0", "url-2")}

    def test_new_release_is_added(self):
        self.assertEqual(changes(self.old, store("1.2.0", "1.1.0", "1.0.0")), (["DeckyEQ 1.2.0"], []))

    def test_unchanged_catalog_has_no_changes(self):
        self.assertEqual(changes(self.old, store("1.1.0", "1.0.0")), ([], []))

    def test_missing_old_release_is_removed(self):
        self.assertEqual(changes(self.old, store("1.1.0")), ([], ["DeckyEQ 1.0.0"]))


if __name__ == "__main__":
    unittest.main()
