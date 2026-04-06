@regression
Feature: Leave Management - TC05 My Leave Status

  Scenario: Recently applied leave appears in My Leave with pending status
    Given user opens the HRMS login page
    When user logs in with valid credentials from test data
    And user opens Leave Request page
    And user opens create leave request modal for status validation
    And user handles leave balance warning for status validation if shown
    And user enters valid leave details for status validation
    Then the applied leave should appear in My Leave with status Pending for approval
