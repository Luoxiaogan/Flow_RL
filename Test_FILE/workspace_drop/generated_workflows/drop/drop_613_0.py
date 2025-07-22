# Workflow ID: drop_613_0
# Benchmark: drop
# Data Indices: [508, 965, 2297, 3081, 691]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary calculations or comparisons based on extracted data.</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Validate the result against the context of the question to ensure accuracy.</instruction>
  </node>
  <node id="5" type="output">
    <data>final_answer</data>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>