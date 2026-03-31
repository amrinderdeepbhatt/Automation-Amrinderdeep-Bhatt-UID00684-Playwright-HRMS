@smoke @regression
Feature: Authentication - TC01 Valid Login

  Scenario: User can login with valid username and password
    Given user opens the HRMS login page
    When user logs in with valid credentials from test data
    Then user should be redirected to the welcome page
