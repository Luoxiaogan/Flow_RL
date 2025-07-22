# Workflow ID: drop_433_0
# Benchmark: drop
# Data Indices: [559, 251, 1484, 2862]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities or events to compare.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant chronological information from the passage for each event mentioned in the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Determine which event occurred earlier by comparing the dates or time references in the extracted information.</prompt>
  </node>
  <node id="4" type="output">
    <prompt>Return the event that happened first based on the comparison.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>