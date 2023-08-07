import unittest
import os
from consumer import main, create_db  

class TestConsumer(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.db_name = "test_wiki_stats"
        self.exchange_name = "test_edit_events"

    def test_create_db(self):
        # Test if the database is created successfully
        create_db(self.db_name)
        self.assertTrue(os.path.exists(f"db/{self.db_name}.db"))

    def test_message_processing(self):
        # Die logik fürs Testen ist mir nicht klar
        pass

if __name__ == "__main__":
    unittest.main()
