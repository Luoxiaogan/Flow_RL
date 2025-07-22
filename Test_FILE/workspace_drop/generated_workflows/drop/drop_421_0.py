# Workflow ID: drop_421_0
# Benchmark: drop
# Data Indices: [882, 3352, 3366, 382, 529]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="process">
    <description>Parse and understand the question</description>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="process">
    <description>Extract relevant data from passage</description>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="process">
    <description>Apply logical or mathematical reasoning based on extracted data</description>
    <dependencies>3</dependencies>
  </node>
  <node id="5" type="output">
    <description>Generate final answer</description>
    <dependencies>4</dependencies>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>