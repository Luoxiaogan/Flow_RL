# Workflow ID: drop_266_0
# Benchmark: drop
# Data Indices: [3958, 1109, 3316, 3172]

<node id="1" type="input">
    <prompt>Understand the question and identify key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant details from the passage that directly answer the question. Focus only on the necessary facts, avoiding unnecessary context.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Perform calculations or logical reasoning based on the extracted facts to derive the answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the result by cross-checking with the passage to ensure accuracy and completeness.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer in a clear and concise format.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>