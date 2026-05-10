@regression
Feature: Cancel leave request

    Background:
        Given user opens the HRMS login page at "/"
        When user logs in with valid credentials from test data

    Scenario: Cancelled leave request appears on top with valid status
        When user opens "My Leave" page from "Self Service"
        And user cancels leave
        Then cancelled leave appears on top with valid status
