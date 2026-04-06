@regression
Feature: Filter leaves by leave status and applied on date
    
    Scenario: Leave status and applied on date to filter leaves 
        Given user opens the HRMS login page
        When user logs in with valid credentials from test data
        And user opens My Leave page
        And user opens leave filter search
        And user inputs leave status and applied on in column search
        Then leaves should be filtered by leave status and applied on date
        