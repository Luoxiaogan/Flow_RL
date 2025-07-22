# Workflow ID: drop_699_0
# Benchmark: drop
# Data Indices: [2713, 1558, 707, 880, 83]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements to extract from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage that directly answers the question. Focus on chronological events, names, and specific actions.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted information matches the question's requirement — e.g., identifying the first touchdown scorer in a game or a time gap between two events.</prompt>
  </node>
  <node id="4" type="operator">
    <prompt>Use logical comparison or sequence analysis to confirm the correct answer based on order or timing (e.g., first, last, or time difference).</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer as a concise string, ensuring it is unambiguous and directly addresses the question.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>