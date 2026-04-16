@smoke @regression
Feature: Authentication - TC01 Login

  Scenario Outline: User can login with valid or invalid credentials
    Given user opens the HRMS login page
    When user logs in with <profile> credentials from test data
    Then user should see <expected_result>

    Examples:
      | profile | expected_result                 |
      | valid   | redirected to the welcome page  |
      | invalid | invalid login error             |
 