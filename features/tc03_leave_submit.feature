@regression
Feature: Leave Management - TC03 Submit Leave Request

  Scenario: User submits leave request with valid required details
    Given user opens the HRMS login page
    When user logs in with valid credentials from test data
    And user opens Leave Request page
    And user opens create leave request modal from Apply Leave
    And user handles leave balance warning if shown
    And user enters leave details with valid date range
    Then user should see leave request submission success
