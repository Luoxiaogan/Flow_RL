# Workflow ID: drop_282_0
# Benchmark: drop
# Data Indices: [708, 2309, 459, 3741, 2652]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key question and relevant data in the passage.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Extract numerical values related to the question from the passage.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Compare values if multiple are present (e.g., percentages, counts).</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="agent">
    <instruction>Determine which group is larger based on comparison.</instruction>
    <depends_on>4</depends_on>
  </node>
  <node id="6" type="output">
    <instruction>Return the final answer as a string indicating the larger ancestral group.</instruction>
    <depends_on>5</depends_on>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>