# Workflow ID: drop_300_0
# Benchmark: drop
# Data Indices: [2206, 1745, 834, 1001]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="analyze">
    <description>Break down the question and identify required data from passage</description>
  </node>
  <node id="3" type="extract">
    <description>Locate numerical values or percentages relevant to the question</description>
  </node>
  <node id="4" type="compute">
    <description>Perform arithmetic operations (e.g., subtraction, percentage calculation)</description>
  </node>
  <node id="5" type="validate">
    <description>Ensure result is logically consistent with passage context</description>
  </node>
  <node id="6" type="output">
    <description>Return final answer as a number or percentage</description>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>