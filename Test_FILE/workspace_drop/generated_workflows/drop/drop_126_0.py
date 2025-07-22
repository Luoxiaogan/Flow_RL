# Workflow ID: drop_126_0
# Benchmark: drop
# Data Indices: [2488, 3500, 2677, 2222]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="process">
    <operation>analyze_question</operation>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="process">
    <operation>extract_relevant_data</operation>
    <depends_on>1</depends_on>
  </node>
  <node id="4" type="process">
    <operation>calculate_percentage</operation>
    <depends_on>2,3</depends_on>
  </node>
  <node id="5" type="process">
    <operation>compare_with_threshold</operation>
    <depends_on>4</depends_on>
  </node>
  <node id="6" type="process">
    <operation>generate_answer</operation>
    <depends_on>5</depends_on>
  </node>
  <node id="7" type="output">
    <data>final_answer</data>
    <depends_on>6</depends_on>
  </node>
  <edge from="1" to="2"/>
  <edge from="1" to="3"/>
  <edge from="2" to="4"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>
  <edge from="6" to="7"/>