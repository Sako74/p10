# -*- coding: utf-8 -*-
# +
import sys
import warnings
import unittest

sys.path.append("../")
from utils import *

warnings.filterwarnings("ignore", category=DeprecationWarning)


# -

class StagingTestCase(unittest.TestCase):
    SLOTS = "staging"
    
    def test_detect_none_intent(self):
        pred = get_prediction(
            True,
            "Hello! How are you? I love planes."
        )
        
        self.assertEqual(pred["prediction"]["top_intent"], "None")
    
    def test_detect_none_intent(self):
        pred = get_prediction(
            True,
            "I want to go from Paris to London the 25/12/2021 and stay one week. I have only 512€."
        )
        
        self.assertEqual(pred["prediction"]["top_intent"], "book_flight")

if __name__ == '__main__':
    unittest.main()
