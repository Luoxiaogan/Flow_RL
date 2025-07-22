# Workflow ID: drop_830_0
# Benchmark: drop
# Data Indices: [2856, 2874, 2873, 736, 327]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Extract key events and scoring details from the passage. Focus on identifying all touchdowns scored in the first half.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>Identify which plays occurred in the first half based on the timeline of events described in the passage.</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Filter for only those plays that resulted in touchdowns during the first half, excluding any second-half scoring.</instruction>
  </node>
  <node id="5" type="agent">
    <instruction>Count the number of such touchdowns to determine the final answer.</instruction>
  </node>
  <node id="6" type="output">
    <description>Return the total number of touchdowns scored in the first half.</description>
  </node>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>