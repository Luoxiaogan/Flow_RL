# Workflow ID: drop_205_0
# Benchmark: drop
# Data Indices: [3656, 3809, 552, 3364, 875]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="process">
    <description>Extract relevant data from passage</description>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="compute">
    <description>Perform required calculation or comparison</description>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="validate">
    <description>Verify correctness of result</description>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <description>Return final answer</description>
    <depends_on>4</depends_on>
  </node>