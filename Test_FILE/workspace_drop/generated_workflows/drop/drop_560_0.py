# Workflow ID: drop_560_0
# Benchmark: drop
# Data Indices: [2482, 3975, 2163, 2796]

<node id="1" type="input">
    <prompt>Understand the question and identify key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical data from the passage related to the question. Think step by step: locate all instances of the subject (e.g., field goals, troops, years) and their values.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Perform necessary calculations based on extracted data (e.g., summing yardages, subtracting groups, calculating duration).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that the calculation aligns with the question's requirements and ensures no data is missed or misinterpreted.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer as a single number or value.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>