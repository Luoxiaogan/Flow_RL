# Workflow ID: drop_326_0
# Benchmark: drop
# Data Indices: [951, 205, 1130, 139, 208]

<node id="1" type="input">
    <prompt>Understand the question and identify what needs to be extracted from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify all field goals mentioned in the passage, including distances and kickers if specified.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>For each field goal, determine whether it was successful or missed based on context (e.g., "kicked a 34-yard field goal" implies made; no mention of miss = made).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Count how many field goals were missed. If no misses are explicitly stated, assume zero.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the total number of missed field goals.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>