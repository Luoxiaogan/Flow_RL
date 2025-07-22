# Workflow ID: drop_605_0
# Benchmark: drop
# Data Indices: [2024, 15, 1840, 1815]

<node id="1">
    <instruction>Identify all touchdown passes mentioned in the passage and extract their yardages.</instruction>
    <output>list of yardages</output>
  </node>
  <node id="2">
    <instruction>Find the maximum and minimum values from the list of yardages.</instruction>
    <output>max_yardage, min_yardage</output>
  </node>
  <node id="3">
    <instruction>Calculate the difference between the longest and shortest touchdown pass yardages.</instruction>
    <output>difference</output>
  </node>
  <node id="4">
    <instruction>Return the calculated difference as the final answer.</instruction>
    <output>final_answer</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>