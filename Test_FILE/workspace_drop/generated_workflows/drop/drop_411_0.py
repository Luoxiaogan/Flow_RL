# Workflow ID: drop_411_0
# Benchmark: drop
# Data Indices: [1604, 2998, 1915, 2630, 1067]

<operator id="0">
    <instruction>Identify the key elements in the question and determine what information is needed to answer it.</instruction>
    <input>question</input>
    <output>key_elements</output>
  </operator>
  <operator id="1">
    <instruction>Extract all relevant data from the passage that relates to the key elements identified.</instruction>
    <input>passage, key_elements</input>
    <output>relevant_data</output>
  </operator>
  <operator id="2">
    <instruction>Process the relevant data to isolate the specific answer to the question.</instruction>
    <input>relevant_data</input>
    <output>answer_candidate</output>
  </operator>
  <operator id="3">
    <instruction>Verify the answer candidate against the original question to ensure accuracy and completeness.</instruction>
    <input>question, answer_candidate</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>