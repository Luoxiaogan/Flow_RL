# Workflow ID: drop_238_0
# Benchmark: drop
# Data Indices: [2045, 3834, 1117, 57, 2675]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary calculations or comparisons based on the extracted data.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Validate the result against the question's requirements and ensure correctness.</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <connect_to>4</connect_to>
  </node>