# Workflow ID: drop_675_0
# Benchmark: drop
# Data Indices: [983, 2331, 2889, 1160]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that directly answers the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary calculations using the extracted data to compute the final answer.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="output">
    <connect_to>3</connect_to>
  </node>