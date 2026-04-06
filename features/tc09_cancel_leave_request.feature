@regression
Feature: Cancel leave request

    Scenario: Cancelled leave request appears on top with valid status
        Given user opens the HRMS login page
        When user logs in with valid credentials from test data
        And user opens My Leave page
        And user cancels leave
        Then cancelled leave appears on top with valid status
        