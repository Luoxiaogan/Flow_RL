# Workflow ID: drop_595_0
# Benchmark: drop
# Data Indices: [3272, 2926, 1393, 2200, 2136]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage based on the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary calculations or comparisons using the extracted data to answer the question step by step.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Validate the result by cross-referencing with the passage to ensure accuracy.</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <connects_to>4</connects_to>
  </node>