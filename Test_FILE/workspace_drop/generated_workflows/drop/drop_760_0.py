# Workflow ID: drop_760_0
# Benchmark: drop
# Data Indices: [2714, 219, 2977, 1441]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Read the passage carefully and identify the key events related to the question. Break down the passage into chronological or thematic segments to locate the relevant information.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Based on the segmented information, determine which specific event answers the question. Ensure that the answer is directly supported by the passage without inference beyond what is stated.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the extracted answer matches the exact wording or concept required by the question. If multiple candidates exist, select the one that most precisely fits the query.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>