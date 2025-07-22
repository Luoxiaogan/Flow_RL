# Workflow ID: drop_798_0
# Benchmark: drop
# Data Indices: [1603, 2508, 930, 1225]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Compare the extracted values to determine which group or player meets the criteria in the question.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the comparison result against the passage to ensure accuracy.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>