# Workflow ID: drop_519_0
# Benchmark: drop
# Data Indices: [395, 1750, 3178, 3457, 858]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary calculations or comparisons based on the extracted data to answer the question step by step.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the correctness of the calculated result using logical consistency checks.</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <connect_to>4</connect_to>
  </node>