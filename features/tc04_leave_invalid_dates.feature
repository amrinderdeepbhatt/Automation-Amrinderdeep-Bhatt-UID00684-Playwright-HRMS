@regression
Feature: Leave Management - TC04 Invalid Date Range

  Scenario: System blocks leave submission when To date is less than From date
    Given user opens the HRMS login page
    When user logs in with valid credentials from test data
    And user opens Leave Request page
    And user opens create leave request modal from Apply Leave
    And user handles leave balance warning if shown
    And user selects leave type for invalid date validation
    And user enters leave dates with from offset 12 and to offset 5
    And user submits leave request with invalid date range
    Then user should see invalid to-date validation error
