# Workflow ID: drop_4_0
# Benchmark: drop
# Data Indices: [1646, 2390, 515, 3841, 1244]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="process">
    <operation>extract_percentage_data</operation>
    <dependencies>[1]</dependencies>
  </node>
  <node id="3" type="process">
    <operation>calculate_not_in_range</operation>
    <dependencies>[2]</dependencies>
  </node>
  <node id="4" type="output">
    <data>result</data>
    <dependencies>[3]</dependencies>
  </node>