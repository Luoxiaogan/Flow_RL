# Workflow ID: drop_833_0
# Benchmark: drop
# Data Indices: [3083, 3050, 426, 971]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Extract key numerical data from the passage relevant to the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific values or time periods mentioned in the passage that relate to the question.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Perform necessary arithmetic or logical operations to derive the answer based on extracted values.</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <instruction>Return the final computed answer.</instruction>
    <depends_on>4</depends_on>
  </node>