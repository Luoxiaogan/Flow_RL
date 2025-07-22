# Workflow ID: drop_588_0
# Benchmark: drop
# Data Indices: [3856, 3204, 2068, 1930, 3428]

<node id="1" type="input">
    <description>Receive problem input</description>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key entities and numerical data relevant to the question. Extract all values mentioned in the passage that relate to the query.</instruction>
  </node>
  <node id="3" type="agent">
    <instruction>For problems involving averages or totals, compute the necessary arithmetic operations step by step using the extracted values.</instruction>
  </node>
  <node id="4" type="agent">
    <instruction>Determine whether the question requires a direct value, a percentage calculation, or a comparison between values. Apply logical reasoning accordingly.</instruction>
  </node>
  <node id="5" type="agent">
    <instruction>Verify the computed result against the passage to ensure accuracy and consistency with the context provided.</instruction>
  </node>
  <node id="6" type="output">
    <description>Return the final answer based on the verified computation.</description>
  </node>

  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>