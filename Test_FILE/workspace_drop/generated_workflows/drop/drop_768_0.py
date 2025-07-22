# Workflow ID: drop_768_0
# Benchmark: drop
# Data Indices: [324, 88, 2152, 1247, 672]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Compare the extracted values to determine the answer to the question.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the logic and ensure the final answer matches the question's requirement.</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <depends_on>4</depends_on>
  </node>