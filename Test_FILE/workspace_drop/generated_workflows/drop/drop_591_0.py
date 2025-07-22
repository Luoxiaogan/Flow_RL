# Workflow ID: drop_591_0
# Benchmark: drop
# Data Indices: [3440, 1246, 6, 2177, 1413]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Identify key numerical or percentage data in the passage relevant to the question.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Calculate derived values if needed (e.g., percentages, totals, differences).</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the computed value matches the question's requirement exactly.</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <description>Return the final answer as a number or percentage.</description>
    <depends_on>4</depends_on>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>