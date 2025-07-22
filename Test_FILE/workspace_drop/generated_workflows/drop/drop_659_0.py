# Workflow ID: drop_659_0
# Benchmark: drop
# Data Indices: [108, 2227, 2087, 1737]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="process">
    <operation>extract_percentages</operation>
  </node>
  <node id="3" type="filter">
    <condition>value > 24</condition>
  </node>
  <node id="4" type="output">
    <format>list of percentages</format>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>