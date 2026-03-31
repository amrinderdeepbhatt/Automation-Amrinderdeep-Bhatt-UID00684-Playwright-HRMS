@regression
Feature: Employee search by UID in HR section

  Scenario: User can locate a specific employee using Employee UID
    Given user is logged into HRMS and navigates to HR section
    When user searches for an employee using a valid Employee UID
    Then the system should display the matching employee record