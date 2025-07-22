# Workflow ID: drop_757_0
# Benchmark: drop
# Data Indices: [1477, 3257, 2921, 163]

<node id="1" type="input">
    <prompt>Read the passage carefully and identify all touchdown passes mentioned.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract each touchdown pass detail: passer, receiver, and yardage. Think step by step to ensure no pass is missed.</prompt>
  </node>
  <node id="3" type="operator">
    <prompt>Filter only touchdown passes; ignore field goals, safeties, and other scoring plays.</prompt>
  </node>
  <node id="4" type="operator">
    <prompt>Find the maximum yardage among all extracted touchdown passes.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Identify which passer threw the longest touchdown pass based on the yardage found in node 4.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Return the name of the quarterback who threw the longest touchdown pass.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>