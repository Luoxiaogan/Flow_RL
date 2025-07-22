# Workflow ID: drop_29_0
# Benchmark: drop
# Data Indices: [1509, 2996, 149, 1448, 2602]

<node id="1" type="input">
    <prompt>Understand the question and identify key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant data from the passage that directly answers the question. Focus on numerical values, comparisons, or specific events mentioned.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Perform necessary calculations or logical reasoning using the extracted data (e.g., subtraction for differences, comparison for sizes).</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the result by cross-checking with the passage to ensure accuracy and relevance.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the verified result.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>