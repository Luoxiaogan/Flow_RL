# Workflow ID: drop_771_0
# Benchmark: drop
# Data Indices: [3674, 845, 1336, 1239, 1842]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the relevant information in the passage related to the question.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Extract numerical or categorical data that directly answers the question.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Compare or calculate based on extracted data if needed.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Provide the final answer based on processed data.</prompt>
    <depends_on>4</depends_on>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>