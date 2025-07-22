# Workflow ID: drop_789_0
# Benchmark: drop
# Data Indices: [3202, 763, 1278, 1947]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="process">
    <operation>extract_relevant_data</operation>
    <input>1</input>
  </node>
  <node id="3" type="process">
    <operation>calculate_percentage</operation>
    <input>2</input>
  </node>
  <node id="4" type="output">
    <data>result</data>
    <input>3</input>
  </node>