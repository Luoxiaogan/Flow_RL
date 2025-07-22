# Workflow ID: drop_740_0
# Benchmark: drop
# Data Indices: [524, 2369, 2296, 1939]

<node id="1" type="input">
    <prompt>Understand the question and extract key temporal or quantitative relationships from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the relevant events or values in the passage that relate to the question. Think step by step: first locate the two points of interest, then determine their difference or order.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Calculate the difference between the two values if it's a "how many more" question, or determine the chronological order if it's about timing.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that the calculation or ordering is consistent with the passage details and matches the question precisely.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the verified result from the previous step.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>