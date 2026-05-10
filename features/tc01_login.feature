@smoke @regression
Feature: Authentication - TC01 Login

  Scenario: User can login with valid credentials
    Given user opens the HRMS login page at "/"
    When user logs in with valid credentials from test data
    Then user should be redirected to the welcome page

  Scenario: User sees an invalid login error
    Given user opens the HRMS login page at "/"
    When user logs in with invalid credentials from test data
    Then user should see an invalid login error
