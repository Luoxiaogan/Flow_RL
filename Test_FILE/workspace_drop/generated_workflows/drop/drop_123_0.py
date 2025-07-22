# Workflow ID: drop_123_0
# Benchmark: drop
# Data Indices: [2122, 2858, 2340, 2916]

<node id="1" type="input">
    <prompt>Understand the question and identify key numerical values.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract relevant data from the passage that relates to the question.</prompt>
  </node>
  <node id="3" type="compute">
    <prompt>Perform necessary arithmetic or comparison operations.</prompt>
  </node>
  <node id="4" type="validate">
    <prompt>Verify the computed result aligns with the passage context.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on validated computation.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>