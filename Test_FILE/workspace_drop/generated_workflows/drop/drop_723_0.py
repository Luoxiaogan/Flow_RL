# Workflow ID: drop_723_0
# Benchmark: drop
# Data Indices: [1266, 2584, 2489, 3, 409]

<node id="1" type="input">
    <instruction>Extract relevant information from the passage related to the question.</instruction>
  </node>
  <node id="2" type="process">
    <instruction>Identify all instances of the specified event (e.g., touchdown passes, field goals, etc.) in the passage.</instruction>
  </node>
  <node id="3" type="filter">
    <instruction>Filter results based on the condition in the question (e.g., shorter than 13 yards, 50+ yards, etc.).</instruction>
  </node>
  <node id="4" type="count">
    <instruction>Count the number of valid instances that meet the condition.</instruction>
  </node>
  <node id="5" type="output">
    <instruction>Return the final count as the answer to the question.</instruction>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>