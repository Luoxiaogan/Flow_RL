# Workflow ID: drop_26_0
# Benchmark: drop
# Data Indices: [3595, 1584, 1220, 2432, 765]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="process">
    <operation>extract_relevant_data</operation>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="process">
    <operation>calculate_percentage</operation>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="validate">
    <operation>check_consistency</operation>
    <dependencies>3</dependencies>
  </node>
  <node id="5" type="output">
    <operation>format_result</operation>
    <dependencies>4</dependencies>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>