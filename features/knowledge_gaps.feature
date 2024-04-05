# 4. Identify knowledge gaps.
# Use CLI -> initiate the process by selecting a topic ->
# it then uses embeddings and OpenAI to select unanswered questions about that topic ->
# unanswered questions are posted to specific slack channel -> users can answer them in threads ->
# bookmarked conversations are uploaded to Confluence (dedicated space).

# Ask NOT DX question ("What power superman has?").
# Wait for answer in thread.
# TA should answer that it has no context about it.
# Check qa_interactions table about this question exists.

# Go to MAIN console menu:

# press 3 (Create a vector db for interactions)
# check that all rows in qa_interactions table have last_embeded and embed filled in.

# Go to MAIN console menu:

# press 5 (Identify knowledge gaps)
# enter "superman"
# TA should post a message in topassist-dev-knowledge-gap channel
# check that quiz_questions last row has a thread_id

# Use white_check_mark emoji on TA message
# check that user in user_scores table appears and has filled luminary_score eq 1

Feature: Knowledge gaps

  Scenario: TopAssist initiates conversations for unanswered questions
    Given databases contain documents with associated embeddings:
      | title           | contents                                                  |
      | Holiday Policy  | Full time employees are eligible for 30 days of per year. |
      | Hardware Policy | Company hardware cannot be used for personal purposes.    |
    When I submit phrase: "What power superman has?"
    Then listener asks OpenAI for embeddings for the given phrase
    And corresponding documents are not found in the database
    And question "What power superman has?" is saved as unanswered
    And I get rewarded 1 revealer point
    When I run CLI command "main.py knowledge-gap superman"
    Then listener asks OpenAI for embeddings for the given phrase
    And unanswered questions for given embeddings are found:
      | question                 |
      | What power superman has? |
    And thread "What power superman has?" is created in #topassist-dev-knowledge-gap channel
    When I reply in the thread with: "Flying"
    And I react to that reply with :white_check_mark:
    Then conversation is being uploaded to dedicated confluence space
    And I am awarded 1 luminary point
