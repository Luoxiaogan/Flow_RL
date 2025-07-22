# Workflow ID: drop_74_0
# Benchmark: drop
# Data Indices: [3338, 2193, 3121, 2620]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical values and relationships in the problem. Break down the question to determine what needs to be calculated or compared.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Extract relevant data from the passage that directly answers the question. Focus only on numbers, categories, or comparisons mentioned in the question.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Perform the necessary arithmetic or logical operation based on the extracted data. Ensure accuracy by double-checking the steps.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="output">
    <instruction>Return the final answer derived from the previous step. Do not include any extra explanation or text.</instruction>
    <input>4</input>
  </node>