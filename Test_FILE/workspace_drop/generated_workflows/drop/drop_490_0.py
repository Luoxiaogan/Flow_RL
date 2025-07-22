# Workflow ID: drop_490_0
# Benchmark: drop
# Data Indices: [3012, 3524, 130, 2837]

<node id="1" type="input">
    <prompt>Understand the question and extract key temporal information.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the start and end years of the relevant period from the passage.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Calculate the duration by subtracting the start year from the end year.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="output">
    <prompt>Return the total number of years as the final answer.</prompt>
    <depends_on>3</depends_on>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>