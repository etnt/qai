import unittest
from qutils import extract_json_objects

class TestJsonExtractor(unittest.TestCase):
    def test_extract_json_objects(self):
        # Example of output from the LLM that contains JSON-like text
        example_text = """
        Action:
        {
            'action': 'search',
            'action_input': {
                'query': 'Nobel Prize in Literature 2023 winner'
            }
        }
        """

        # Convert it to proper JSON format
        json_text = example_text.replace("'", '"')

        # Extract JSON objects
        data = list(extract_json_objects(json_text))

        # Check that the extracted data is correct
        self.assertEqual(data, [{'action': 'search', 'action_input': {'query': 'Nobel Prize in Literature 2023 winner'}}])

if __name__ == '__main__':
    unittest.main()