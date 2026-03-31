@regression
Feature: Leave Management - TC03 Submit Leave Request

  Scenario: User submits leave request with valid required details
    Given user logs into HRMS and opens Leave Request page
    When user opens create leave request modal from Apply Leave
    And user handles leave balance warning if shown
    And user enters leave details with valid date range and submits form
    Then leave request should be submitted successfully
