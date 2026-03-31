@regression
Feature: Authentication - TC02 Invalid Login

  Scenario: System shows proper error on invalid credentials
    Given user opens the HRMS login page for invalid login
    When user logs in with invalid credentials from test data
    Then user should see invalid login error
