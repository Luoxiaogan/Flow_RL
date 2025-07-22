# Workflow ID: drop_53_0
# Benchmark: drop
# Data Indices: [966, 62, 2729, 2457]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Think step by step to identify the key data relevant to the question. Extract numerical values and percentages from the passage that directly relate to the query.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Calculate the required percentage or value based on the extracted data. Ensure mathematical accuracy and logical consistency with the question's requirements.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the result by cross-checking against the original passage. Confirm that no misinterpretation or omission occurred during calculation.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>