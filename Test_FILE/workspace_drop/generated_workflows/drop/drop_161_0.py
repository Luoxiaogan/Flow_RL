# Workflow ID: drop_161_0
# Benchmark: drop
# Data Indices: [3540, 3727, 3279, 3943]

<node id="1" type="input">
    <prompt>Understand the question and identify the key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical data from the passage that directly answers the question. Think step by step: first locate where the answer is mentioned, then identify the exact value.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted number matches the question's context (e.g., field goal distance, time interval, population count, etc.). If not, recheck the passage for the correct data.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the final numerical answer based on the verified extraction.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>