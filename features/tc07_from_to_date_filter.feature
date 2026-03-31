@regression
Feature: From To Date Filter

    Scenario: From To Date filter narrows down leave records in selected time frame
        Given user logs into HRMS and opens my leave page
        When user clicks on search and filters by filling from and to dates
        Then leave records should be filtered in selected timeframe