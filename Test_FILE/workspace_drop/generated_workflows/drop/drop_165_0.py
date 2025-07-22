# Workflow ID: drop_165_0
# Benchmark: drop
# Data Indices: [1209, 3339, 3300, 2613, 3594]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage based on the question.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Perform arithmetic or percentage calculations using the extracted data.</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Validate the calculation logic and ensure it matches the question's requirement.</instruction>
  </node>
  <node id="5" type="output">
    <data>final_answer</data>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>