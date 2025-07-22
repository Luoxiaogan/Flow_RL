# Workflow ID: drop_544_0
# Benchmark: drop
# Data Indices: [827, 1923, 1849, 1007]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="process">
    <operation>Extract relevant data from passage</operation>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="process">
    <operation>Perform calculation based on extracted data</operation>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="output">
    <operation>Return final answer</operation>
    <depends_on>3</depends_on>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>