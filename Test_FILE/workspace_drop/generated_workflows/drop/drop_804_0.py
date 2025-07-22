# Workflow ID: drop_804_0
# Benchmark: drop
# Data Indices: [3739, 2367, 1358, 3970]

<node id="1" type="input">
    <prompt>Understand the question and identify the key information needed to solve it.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant data from the passage related to the question. Focus only on the specific details required.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Process the extracted data to determine the answer. Apply logical reasoning or simple arithmetic if needed.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="output">
    <prompt>Provide the final answer based on the processed result.</prompt>
    <depends_on>3</depends_on>
  </node>