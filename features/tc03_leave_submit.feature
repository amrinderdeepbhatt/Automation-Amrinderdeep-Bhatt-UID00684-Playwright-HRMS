@regression
Feature: Leave Management - TC03 Submit Leave Request

  Background:
    Given user opens the HRMS login page at "/"
    When user logs in with valid credentials from test data

  Scenario: User submits leave request with valid required details
    When user navigates to "Self Service" from navigation bar
    And user opens create leave request modal from Apply Leave
    And user enters leave details with valid date range
    Then user should see leave request submission success
