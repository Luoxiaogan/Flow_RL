# Workflow ID: drop_403_0
# Benchmark: drop
# Data Indices: [2733, 3124, 134, 284]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform arithmetic operations to compute the final answer based on extracted data.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="output">
    <instruction>Return the computed result as the final answer.</instruction>
    <input>3</input>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>