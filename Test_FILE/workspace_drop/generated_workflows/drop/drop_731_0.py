# Workflow ID: drop_731_0
# Benchmark: drop
# Data Indices: [2415, 434, 2536, 2876, 1305]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="process">
    <description>Extract relevant percentages from passage</description>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="logic">
    <description>Apply arithmetic to compute required percentage</description>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="output">
    <description>Return the computed percentage</description>
    <dependencies>3</dependencies>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>