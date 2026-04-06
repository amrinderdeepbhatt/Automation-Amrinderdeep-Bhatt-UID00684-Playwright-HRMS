@regression
Feature: From To Date Filter

    Scenario: From To Date filter narrows down leave records in selected time frame
        Given user opens the HRMS login page
        When user logs in with valid credentials from test data
        And user opens My Leave page
        And user opens leave filter search
        And user fills from and to dates for leave filter
        Then leave records should be filtered in selected timeframe
        