# Workflow ID: drop_751_0
# Benchmark: drop
# Data Indices: [2545, 946, 813, 1035, 2438]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Extract the key question from the problem statement.</instruction>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <instruction>Identify and locate the relevant information in the passage that answers the key question.</instruction>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <instruction>Verify if the extracted answer is directly supported by the passage, and resolve any ambiguity.</instruction>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="agent">
    <instruction>Format the final answer to match the expected output structure (e.g., number, name, etc.).</instruction>
    <depends_on>4</depends_on>
  </node>
  <node id="6" type="output">
    <data>5</data>
    <depends_on>5</depends_on>
  </node>