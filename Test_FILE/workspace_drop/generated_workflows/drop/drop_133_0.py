# Workflow ID: drop_133_0
# Benchmark: drop
# Data Indices: [142, 3413, 1022, 1661]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical values from the passage related to the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Perform the necessary arithmetic operations based on the extracted values to answer the question.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="output">
    <param name="answer">The result of the calculation from node 3.</param>
    <depends_on>3</depends_on>
  </node>