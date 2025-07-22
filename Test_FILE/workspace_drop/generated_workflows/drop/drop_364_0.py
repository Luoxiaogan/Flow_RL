# Workflow ID: drop_364_0
# Benchmark: drop
# Data Indices: [3657, 817, 1009, 2175, 3983]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="analyze">
    <description>Parse and understand the question and passage</description>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="extract">
    <description>Identify relevant numerical data from passage</description>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="compute">
    <description>Perform percentage calculation or comparison</description>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="validate">
    <description>Verify correctness of computed result</description>
    <depends_on>4</depends_on>
  </node>
  <node id="6" type="output">
    <description>Return final answer</description>
    <depends_on>5</depends_on>
  </node>