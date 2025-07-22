# Workflow ID: drop_479_0
# Benchmark: drop
# Data Indices: [829, 2305, 2106, 123, 1845]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements to track.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant events or actions from the passage that relate to the question. Focus on chronological order or numerical values if applicable.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare or calculate based on extracted data—e.g., determine which event happened second, or compute totals.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that your answer matches the question’s requirement exactly (e.g., time, quantity, sequence).</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer as a concise response based on the previous steps.</prompt>
  </node>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>