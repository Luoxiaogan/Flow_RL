# Workflow ID: drop_143_0
# Benchmark: drop
# Data Indices: [454, 1238, 1114, 2683]

<node id="1" type="input">
    <description>Receive problem statement and passage</description>
  </node>
  
  <node id="2" type="process">
    <description>Extract relevant numerical data from passage</description>
    <dependencies>1</dependencies>
  </node>
  
  <node id="3" type="process">
    <description>Identify the key comparison or calculation required</description>
    <dependencies>2</dependencies>
  </node>
  
  <node id="4" type="process">
    <description>Perform arithmetic operations (e.g., subtraction, summation)</description>
    <dependencies>3</dependencies>
  </node>
  
  <node id="5" type="output">
    <description>Return final answer based on computed result</description>
    <dependencies>4</dependencies>
  </node>
  
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>