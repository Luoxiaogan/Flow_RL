# Workflow ID: drop_445_0
# Benchmark: drop
# Data Indices: [1313, 2849, 3525, 2394]

<node id="1" type="input">
    <prompt>Extract relevant numerical data from the passage related to the question.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Identify the key metric (e.g., percentage, yardage, count) that answers the question.</prompt>
  </node>
  <node id="3" type="compare">
    <prompt>Compare values to determine the second most common category or the difference between two values.</prompt>
  </node>
  <node id="4" type="aggregate">
    <prompt>Sum or tally relevant counts if multiple instances are involved (e.g., field goals by team).</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the processed comparison or aggregation.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>