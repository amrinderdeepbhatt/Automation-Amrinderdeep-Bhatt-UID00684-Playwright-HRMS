@regression
Feature: Employee search by UID in HR section

  Background:
    Given user opens the HRMS login page at "/"
    When user logs in with valid credentials from test data

  Scenario: User can locate a specific employee using Employee UID
    When user navigates to "HR" from navigation bar
    And user selects Employee UID search type
    And user enters a valid Employee UID
    And user clicks employee search button
    Then the system should display the matching employee record
