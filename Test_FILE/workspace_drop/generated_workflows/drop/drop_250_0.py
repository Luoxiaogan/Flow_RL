# Workflow ID: drop_250_0
# Benchmark: drop
# Data Indices: [2952, 3256, 3543, 3604, 2510]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="process">
    <description>Parse and extract key data points relevant to the question</description>
  </node>
  <node id="3" type="logic">
    <description>Apply logical reasoning based on extracted data</description>
  </node>
  <node id="4" type="validate">
    <description>Verify that the solution aligns with all provided constraints</description>
  </node>
  <node id="5" type="output">
    <description>Return final answer</description>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>