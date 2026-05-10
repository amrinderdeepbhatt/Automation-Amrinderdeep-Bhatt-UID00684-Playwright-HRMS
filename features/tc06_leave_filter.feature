@regression
Feature: Filter and Action - Leave filter by keyword

    Background:
        Given user opens the HRMS login page at "/"
        When user logs in with valid credentials from test data

    Scenario Outline: Leave filter result when searching by specific keywords
        When user opens "My Leave" page from "Self Service"
        And user opens leave filter search
        And user enters <keyword> in Leave Type filter
        Then leave data should be filtered as per the entered keyword

    Examples:
        | keyword |
        | Sick    |
        | Annual  |
