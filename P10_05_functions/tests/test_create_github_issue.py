import unittest

import azure.functions as func
from create_github_issue import main


class CreateGithubIssueTestCase(unittest.TestCase):
    NAME = "You"

    def test_create_github_issue(self):
        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method='GET',
            body=None,
            url='/api/create_github_issue',
            params={'name': self.NAME})

        # Call the function.
        resp = main(req)

        # Check the output.
        self.assertEqual(
            resp.get_body().decode("utf-8"),
            f"Hello, {self.NAME}. This HTTP triggered function executed successfully."
        )

if __name__ == '__main__':
    unittest.main()