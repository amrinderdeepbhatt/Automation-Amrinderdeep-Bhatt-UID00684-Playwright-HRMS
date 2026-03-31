@regression
Feature: Leave Management - TC05 My Leave Status

  Scenario: Recently applied leave appears in My Leave with pending status
    Given user logs into HRMS and opens Leave Request page for status validation
    When user applies a valid leave request for status validation
    Then the applied leave should appear in My Leave with status Pending for approval
