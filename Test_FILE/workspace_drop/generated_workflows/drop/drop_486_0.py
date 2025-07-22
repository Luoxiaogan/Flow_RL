# Workflow ID: drop_486_0
# Benchmark: drop
# Data Indices: [2302, 3515, 217, 1168]

<node id="1" type="input">
    <prompt>Understand the problem and identify key data points.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical values from the passage related to the question.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the extracted values to the criteria specified in the question.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Determine which value(s) satisfy the condition in the question.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the filtered values.</prompt>
    <depends_on>4</depends_on>
  </node>