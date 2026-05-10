@regression
Feature: From To Date Filter

    Background:
        Given user opens the HRMS login page at "/"
        When user logs in with valid credentials from test data

    Scenario: From To Date filter narrows down leave records in selected time frame
        When user opens "My Leave" page from "Self Service"
        And user opens leave filter search
        And user fills from and to dates for leave filter
        Then leave records should be filtered in selected timeframe
