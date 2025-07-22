# Workflow ID: drop_309_0
# Benchmark: drop
# Data Indices: [378, 3679, 669, 3887]

<node id="1" type="input">
    <prompt>Understand the question and identify key elements to extract from the passage.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the passage that directly answers the question. Focus on dates, events, and numerical values as needed.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Perform necessary calculations or comparisons based on extracted data to derive the answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the logic of the calculation or comparison to ensure accuracy and alignment with the question.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer in a clear and concise format.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>