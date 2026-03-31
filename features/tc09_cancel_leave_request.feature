@regression
Feature: Cancel leave request

    Scenario: Cancelled leave request appears on top with valid status
        Given user logs into HRMS and navigates to My leave page
        When user cancels leave
        Then cancelled leave appears on top with valid status