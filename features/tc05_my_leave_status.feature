@regression
Feature: Leave Management - TC05 My Leave Status

  Background:
    Given user opens the HRMS login page at "/"
    When user logs in with valid credentials from test data

  Scenario: Recently applied leave appears in My Leave with pending status
    When user navigates to "Self Service" from navigation bar
    And user opens create leave request modal for status validation
    And user enters valid leave details for status validation
    Then the applied leave should appear in My Leave with status Pending for approval
