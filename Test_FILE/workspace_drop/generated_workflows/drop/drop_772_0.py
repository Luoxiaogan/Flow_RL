# Workflow ID: drop_772_0
# Benchmark: drop
# Data Indices: [2967, 1293, 3375, 3275, 630]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify the key values that need to be compared or calculated.</instruction>
    <input>1</input>
    <output>2</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform the required arithmetic operation (e.g., subtraction, addition, or comparison) based on the extracted values to answer the question step by step.</instruction>
    <input>2</input>
    <output>3</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the correctness of the calculation and ensure it directly answers the question without introducing irrelevant details.</instruction>
    <input>3</input>
    <output>4</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
  </node>