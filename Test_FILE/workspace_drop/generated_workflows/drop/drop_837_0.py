# Workflow ID: drop_837_0
# Benchmark: drop
# Data Indices: [531, 3560, 1206, 444, 1810]

<node id="1" type="input">
    <prompt>Understand the question and extract key information from the passage.</prompt>
  </node>
  <node id="2" type="operator">
    <prompt>Identify all scoring events in the game and determine which team scored each time.</prompt>
  </node>
  <node id="3" type="operator">
    <prompt>Count how many times the Cowboys scored based on the identified scoring events.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the number of times the Cowboys scored in the game.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>