# 1. Populate knowledge base.
#   Use CLI -> fetch from Confluence (pages with all the comments)
#    -> SQL -> OpenAI generate embeddings -> vector db

Feature: Populate knowledge base

  Scenario: CLI commands invocation pulls data from Confluence and saves it in vector database
    Given Confluence stubs are defined:
      | space | page title      | page contents |
      | IT    | Hardware Policy | Company hardware cannot be used for personal purposes.    |
      | HR    | Holiday Policy  | Full time employees are eligible for 30 days of per year. |
    When I run CLI command "main.py import --space HR"
    Then Confluence documents are stored in SQL database
      | title          |
      | Holiday Policy |
    And binary document representations are stored in vector database
      | title           | embeddings      |
      | Holiday Policy  | <format t.b.d.> |
