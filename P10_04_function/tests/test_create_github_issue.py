import unittest, json
from unittest.mock import patch, MagicMock

from create_github_issue import *


class CreateGithubIssueTestCase(unittest.TestCase):
    ALERT_DATA = {
        "data":{
            "essentials":{
                "description":"High number of insatifactions"
            },
            "alertContext":{
                "condition":{
                    "windowStartTime":"2021-12-20T21:25:13Z",
                    "windowEndTime":"2021-12-20T22:25:13Z"
                }
            }
        }
    }

    @patch('create_github_issue.create_issue')
    def test_create_github_issue(self, mock_create_issue):
        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method='POST',
            url='/api/create_github_issue',
            body=json.dumps(self.ALERT_DATA).encode("utf-8"),
        )

        expected_data = {
            "title": self.ALERT_DATA["data"]["essentials"]["description"],
            "body": {
                "start_dt": self.ALERT_DATA["data"]["alertContext"]["condition"]["windowStartTime"],
                "end_dt": self.ALERT_DATA["data"]["alertContext"]["condition"]["windowEndTime"]
            }
        }

        # Call the function.
        resp = main(req).get_body().decode("utf-8")
        expected_resp = json.dumps(expected_data)

        mock_create_issue.assert_called_once_with(
            expected_data["title"],
            expected_data["body"]
        )

        # Check the output.
        self.assertEqual(resp, expected_resp)

if __name__ == '__main__':
    unittest.main()