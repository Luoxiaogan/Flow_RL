# Workflow ID: drop_697_0
# Benchmark: drop
# Data Indices: [2567, 1884, 3603, 1530]

<node id="1" type="input">
    <prompt>Understand the question and identify key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant data from the passage that directly answers the question. Focus on specific numbers, names, or events mentioned.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Perform necessary calculations or comparisons using the extracted data. For example, if percentages are involved, compute the difference or percentage of non-English speakers.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the result by cross-checking with the original passage to ensure accuracy and avoid misinterpretation.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Provide the final answer based on the verified result. Ensure clarity and correctness.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>