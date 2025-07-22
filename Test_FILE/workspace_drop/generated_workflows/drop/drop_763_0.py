# Workflow ID: drop_763_0
# Benchmark: drop
# Data Indices: [3979, 1669, 1139, 1131]

<node id="1">
    <instruction>Identify all field goals in the passage and extract their yardages.</instruction>
    <output>Field goals: [25, 47, 35, 35]</output>
  </node>
  <node id="2">
    <instruction>Filter field goals that are between 15 and 60 yards (inclusive).</instruction>
    <output>Filtered field goals: [25, 47, 35, 35]</output>
  </node>
  <node id="3">
    <instruction>Count the number of filtered field goals.</instruction>
    <output>Count: 4</output>
  </node>
  <node id="4">
    <instruction>Return the final count as the answer to the question.</instruction>
    <output>4</output>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>