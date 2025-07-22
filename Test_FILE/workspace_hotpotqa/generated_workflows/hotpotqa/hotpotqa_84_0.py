# Workflow ID: hotpotqa_84_0
# Benchmark: hotpotqa
# Data Indices: [2576, 1167, 2690, 3764]

<node id="1" type="input">
    <prompt>Understand the problem and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify which entity in the context matches the question's focus. Think step by step to avoid incorrect associations.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify the relationship between the named entity and the subject (e.g., who was named after whom).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Check for any conflicting or ambiguous information in the context that might affect the answer.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the correct genus based on the verified information.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>