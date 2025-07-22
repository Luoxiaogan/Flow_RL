# Workflow ID: drop_797_0
# Benchmark: drop
# Data Indices: [3336, 1809, 3248, 1925, 2589]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific values or percentages needed to answer the question.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Perform necessary arithmetic operations (e.g., subtraction, percentage calculation).</instruction>
    <input>3</input>
  </node>
  <node id="5" type="agent">
    <instruction>Verify that the calculated result matches the question's requirement.</instruction>
    <input>4</input>
  </node>
  <node id="6" type="output">
    <instruction>Return the final answer as a numeric value.</instruction>
    <input>5</input>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>