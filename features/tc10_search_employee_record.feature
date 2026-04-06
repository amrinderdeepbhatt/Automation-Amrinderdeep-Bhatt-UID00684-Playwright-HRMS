@regression
Feature: Employee search by UID in HR section

  Scenario: User can locate a specific employee using Employee UID
    Given user opens the HRMS login page
    When user logs in with valid credentials from test data
    And user opens HR section
    And user selects Employee UID search type
    And user enters a valid Employee UID
    And user clicks employee search button
    Then the system should display the matching employee record
    