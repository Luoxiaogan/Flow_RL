# Workflow ID: drop_390_0
# Benchmark: drop
# Data Indices: [1919, 3233, 690, 541]

<node id="1" type="input">
    <prompt>Understand the question and identify the key numerical information needed.</prompt>
  </node>
  <node id="2" type="process">
    <prompt>Extract relevant data from the passage that directly answers the question.</prompt>
  </node>
  <node id="3" type="compute">
    <prompt>Perform necessary calculations (e.g., subtraction, comparison) based on extracted data.</prompt>
  </node>
  <node id="4" type="validate">
    <prompt>Verify that the calculation aligns with the context of the question and passage.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer in a clear, concise format.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>