@regression
Feature: Leave Management - TC04 Invalid Date Range

  Background:
    Given user opens the HRMS login page at "/"
    When user logs in with valid credentials from test data

  Scenario: System blocks leave submission when To date is less than From date
    When user navigates to "Self Service" from navigation bar
    And user opens create leave request modal from Apply Leave
    And user selects leave type for invalid date validation
    And user enters leave dates with from offset 12 and to offset 5
    And user submits leave request with invalid date range
    Then user should see invalid to-date validation error
