@regression
Feature: Filter leaves by leave status and applied on date
    
    Scenario: Leave status and applied on date to filter leaves 
        Given user logs into HRMS and navigates to My Leave page
        When user clicks on search button
        And inputs leave status and applied on in column search
        Then leaves should be filtered by leave status and applied on date
        