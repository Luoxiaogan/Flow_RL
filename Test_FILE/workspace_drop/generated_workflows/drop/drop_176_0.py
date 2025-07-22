# Workflow ID: drop_176_0
# Benchmark: drop
# Data Indices: [2467, 2993, 968, 1150, 3084]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities or values to extract.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical data from the passage related to the question. Focus on specific values, events, or counts mentioned directly.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare or count based on extracted data — e.g., total points, number of occurrences, or differences between values.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Validate that all required information is used and no irrelevant details are included in the final answer.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer as a single numerical value or clear statement based on the processed data.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>