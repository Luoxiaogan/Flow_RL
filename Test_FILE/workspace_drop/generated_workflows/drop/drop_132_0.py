# Workflow ID: drop_132_0
# Benchmark: drop
# Data Indices: [500, 2173, 3811, 3556, 902]

<node id="start" type="input"/>
  <node id="analyze" type="agent">
    <instruction>Think step by step: First, identify the key event or data point in the passage that directly answers the question. Then, extract the relevant numerical value or fact. Finally, ensure your answer matches the exact wording of the question.</instruction>
  </node>
  <node id="validate" type="agent">
    <instruction>Verify the extracted information by cross-checking with the passage. Ensure no misinterpretation occurred and that the answer is precise to the question asked.</instruction>
  </node>
  <node id="output" type="output"/>
  <edge from="start" to="analyze"/>
  <edge from="analyze" to="validate"/>
  <edge from="validate" to="output"/>