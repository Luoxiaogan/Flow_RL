# Workflow ID: drop_721_0
# Benchmark: drop
# Data Indices: [761, 286, 3387, 3831, 2450]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary calculations or comparisons based on the extracted data.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Validate the calculation against the context of the question.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="output">
    <instruction>Return the final answer in a clear and concise format.</instruction>
    <input>4</input>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>