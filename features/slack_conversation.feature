Feature: Slack conversation

# 2. Q&A.
#   User posts a message to slack channel the bot is invited to.
#   Slack listener receives the event -> detects if it is a question (if it has ? at the end) ->
#   generates embedding for the question (using OpenAI) -> retrieves most relevant documents from vector database ->
#   builds a message that includes content of relevant pages + user’s question ->
#   creates a conversation with Open AI (thread in an assistant) -> wait for a response ->
#   post to Slack as a response (in a thread) -> store it in database (including association between assistant thread id and slack thread id)
# 3. Feedback. User posts a message to a thread started from the original question -> same as Q&A but instead of creating new conversation it posts to an exiting one.

  Scenario: User interacts with TopAssist in Slack
    Given databases contain documents with associated embeddings:
      | title           | contents                                                  |
      | Holiday Policy  | Full time employees are eligible for 30 days of per year. |
      | Hardware Policy | Company hardware cannot be used for personal purposes.    |
    When I submit phrase: "Totally not a question"
    Then listener  does not react
    When I submit phrase: "How many days off am I eligible for?"
    Then listener asks OpenAI for embeddings for the given phrase
    And corresponding documents are found in the database
    And listener asks OpenAI for answer providing it with
      | question                             | documents                                                 |
      | How many days off am I eligible for? | Full time employees are eligible for 30 days of per year. |
    And this reply is posted in Slack thread: "You are eligible for 30 days off"
    And the reply is saved in the database
    When I submit phrase "Why only 30?"
    Then listener asks OpenAI for embeddings for the given phrase
    And corresponding documents are found in the database
    And listener asks OpenAI for answer providing it with
      | question     | documents                                                 |
      | Why only 30? | Full time employees are eligible for 30 days of per year. |
    And this reply is posted in Slack thread: "That's what's company's Holiday Policy says"
