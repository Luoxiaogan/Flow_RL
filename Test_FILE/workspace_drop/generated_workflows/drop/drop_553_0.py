# Workflow ID: drop_553_0
# Benchmark: drop
# Data Indices: [2476, 482, 3692, 2355]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities or values to extract.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant numerical data from the passage related to the question. Focus on precise values needed for calculation or comparison.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Compare the extracted values to determine the difference, ratio, or other relationship as required by the question.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify that the calculated result aligns with the context of the passage and matches what is being asked.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the verified calculation.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>