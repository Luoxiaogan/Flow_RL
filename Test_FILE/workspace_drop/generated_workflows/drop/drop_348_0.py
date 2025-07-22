# Workflow ID: drop_348_0
# Benchmark: drop
# Data Indices: [447, 1301, 117, 2936]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="process">
    <description>Parse and extract relevant data from the passage</description>
  </node>
  <node id="3" type="process">
    <description>Identify key values or categories based on the question</description>
  </node>
  <node id="4" type="decision">
    <description>Compare values to determine the correct answer</description>
  </node>
  <node id="5" type="output">
    <description>Return the final answer</description>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>