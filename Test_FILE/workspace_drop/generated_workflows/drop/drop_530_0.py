# Workflow ID: drop_530_0
# Benchmark: drop
# Data Indices: [1539, 2655, 1473, 118]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical values and operations required to solve the problem. Break down the question into steps.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Extract relevant percentages, quantities, or values from the passage that relate directly to the question asked.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Apply mathematical operations (e.g., subtraction, percentage calculation) based on the extracted data to compute the answer.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="agent">
    <instruction>Verify that the computed result logically answers the original question without introducing external assumptions.</instruction>
    <input>4</input>
  </node>
  <node id="6" type="output">
    <input>5</input>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>