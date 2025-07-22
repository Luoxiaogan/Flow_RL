# Workflow ID: drop_289_0
# Benchmark: drop
# Data Indices: [778, 573, 1777, 534, 2064]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements to extract from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage that directly answers the question. Focus on numerical values, events, or specific details mentioned in relation to the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare or calculate based on extracted data—e.g., differences, totals, sequences—to derive the final answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that the derived answer matches the question's requirements and aligns with the passage context.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer as a concise, accurate response.</prompt>
  </node>

  <!-- Connections -->
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>