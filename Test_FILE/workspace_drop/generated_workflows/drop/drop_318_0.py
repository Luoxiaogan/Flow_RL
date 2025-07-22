# Workflow ID: drop_318_0
# Benchmark: drop
# Data Indices: [639, 2380, 2953, 549]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical data related to the question. Extract all field goal attempts or successful kicks mentioned in the passage.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Filter only successful field goals from the extracted data. Count each instance where a kicker successfully made a field goal.</instruction>
  </node>
  <node id="4" type="operator">
    <operation>sum</operation>
    <description>Add up all successful field goals identified by Agent 3.</description>
  </node>
  <node id="5" type="output">
    <description>Return the total number of successful field goals.</description>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>