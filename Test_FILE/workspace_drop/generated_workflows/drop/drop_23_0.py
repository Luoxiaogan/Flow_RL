# Workflow ID: drop_23_0
# Benchmark: drop
# Data Indices: [1928, 522, 2448, 3705]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage that directly answers the question. Focus on specific details like names, numbers, or events mentioned in relation to the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify if the extracted information is sufficient to answer the question. If not, look for additional context or clues in the passage that may help infer the correct answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Check for any ambiguity or conflicting data in the passage. Resolve contradictions by prioritizing the most explicit or detailed statement.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Provide a clear and concise final answer based on the verified information from previous steps.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>