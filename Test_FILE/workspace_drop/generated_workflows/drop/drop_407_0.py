# Workflow ID: drop_407_0
# Benchmark: drop
# Data Indices: [2009, 1387, 2319, 3407, 3209]

<node id="1" type="input">
    <prompt>Understand the question and identify key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant details from the passage that directly answer the question. Think step by step: what specific data is required, and where in the text is it located?</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that all necessary elements for solving the question are present in the extracted information. If any piece is missing, flag it as incomplete.</prompt>
  </node>
  <node id="4" type="operator">
    <prompt>Apply logical reasoning or arithmetic operations if needed (e.g., calculating time differences, percentages, totals).</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Ensure the final answer matches the format and precision required by the question—no extra information, no missing parts.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Return the correctly formatted solution based on the processed inputs and reasoning steps.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>