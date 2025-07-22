# Workflow ID: drop_807_0
# Benchmark: drop
# Data Indices: [1408, 2962, 1476, 152]

<operator id="0">
    <instruction>Identify the key event in the passage that answers the question. Focus on the first scoring play mentioned.</instruction>
    <input>problem</input>
    <output>first_scoring_event</output>
  </operator>
  <operator id="1">
    <instruction>Extract the player and scoring method from the first scoring event.</instruction>
    <input>first_scoring_event</input>
    <output>player_and_method</output>
  </operator>
  <operator id="2">
    <instruction>Determine if the scoring event is a touchdown and who scored it.</instruction>
    <input>player_and_method</input>
    <output>answer</output>
  </operator>
  <operator id="3">
    <instruction>Verify that the answer matches the question asked.</instruction>
    <input>answer</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>