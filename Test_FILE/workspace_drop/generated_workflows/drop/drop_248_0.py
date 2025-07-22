# Workflow ID: drop_248_0
# Benchmark: drop
# Data Indices: [2550, 3047, 1268, 2154]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="process">
    <operation>extract_numeric_data</operation>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="process">
    <operation>identify_minimum</operation>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="output">
    <operation>return_result</operation>
    <dependencies>3</dependencies>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>