# Workflow ID: drop_296_0
# Benchmark: drop
# Data Indices: [1318, 2486, 1972, 2720, 3650]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities or values to extract from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage that directly answers the question. Focus on specific details like names, numbers, or events mentioned in relation to the question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare extracted data to determine the correct answer based on context and logical relationships (e.g., longest pass, highest percentage, etc.).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Validate the answer by cross-checking with other parts of the passage to ensure consistency and accuracy.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer clearly and concisely, ensuring it directly addresses the original question.</prompt>
  </node>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>