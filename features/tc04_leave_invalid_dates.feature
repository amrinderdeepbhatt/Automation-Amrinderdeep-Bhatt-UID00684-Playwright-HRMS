@regression
Feature: Leave Management - TC04 Invalid Date Range

  Scenario: System blocks leave submission when To date is less than From date
    Given user logs into HRMS and opens Leave Request page for invalid date validation
    When user opens create leave request modal for invalid date validation
    And user handles leave balance warning for invalid date validation if shown
    And user selects leave type and enters invalid date range where to date is less than from date
    And user submits leave request with invalid date range
    Then user should see invalid to-date validation error
