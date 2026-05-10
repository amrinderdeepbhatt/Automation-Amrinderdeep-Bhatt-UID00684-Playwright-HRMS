@regression
Feature: Filter leaves by leave status and applied on date

    Background:
        Given user opens the HRMS login page at "/"
        When user logs in with valid credentials from test data
    
    Scenario: Leave status and applied on date to filter leaves 
        When user opens "My Leave" page from "Self Service"
        And user opens leave filter search
        And user inputs leave status and applied on in column search
        Then leaves should be filtered by leave status and applied on date
