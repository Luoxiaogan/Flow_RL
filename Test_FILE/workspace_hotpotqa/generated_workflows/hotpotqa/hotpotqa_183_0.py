# Workflow ID: hotpotqa_183_0
# Benchmark: hotpotqa
# Data Indices: [3126, 2666, 3911, 1291, 3360]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context for each entity mentioned in the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the extracted information to determine which entity satisfies the condition in the question.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the comparison result by cross-referencing with additional context clues if available.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the verified result.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>