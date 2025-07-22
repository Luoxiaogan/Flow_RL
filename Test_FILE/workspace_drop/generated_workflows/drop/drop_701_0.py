# Workflow ID: drop_701_0
# Benchmark: drop
# Data Indices: [1869, 3977, 2387, 1599]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Compare values to determine the answer based on the extracted data.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Validate the result by cross-referencing with other data points in the passage.</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <connect_to>4</connect_to>
  </node>