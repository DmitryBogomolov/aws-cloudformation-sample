import unittest
import threading
from .. import parallel

class TestParallel(unittest.TestCase):
    def test_run_parallel(self):
        def do_action_1(a, b):
            return a + b, threading.get_ident()     # pylint: disable=no-member
        def do_action_2(p1, p2):
            return p1 - p2, threading.get_ident()   # pylint: disable=no-member
        results = parallel.run_parallel([
            (do_action_1, (1, 2)),
            (do_action_2, (), {'p1': 10, 'p2': 6}),
            (do_action_1, (10,), {'b': 11})
        ])
        r1, r2, r3 = sorted(results, key=lambda x: x[0])
        self.assertEqual(r1[0], 3)
        self.assertEqual(r2[0], 4)
        self.assertEqual(r3[0], 21)
        ident = threading.get_ident()   # pylint: disable=no-member
        self.assertNotEqual(r1[1], ident)
        self.assertNotEqual(r2[1], ident)
        self.assertNotEqual(r3[1], ident)
