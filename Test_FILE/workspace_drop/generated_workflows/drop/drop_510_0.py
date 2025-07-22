# Workflow ID: drop_510_0
# Benchmark: drop
# Data Indices: [97, 3418, 779, 8]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that pertains to the question.</instruction>
    <dependency>1</dependency>
  </node>
  <node id="3" type="agent">
    <instruction>Perform necessary calculations or comparisons based on the extracted data to answer the question step by step.</instruction>
    <dependency>2</dependency>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the correctness of the calculation by cross-checking with the original passage details.</instruction>
    <dependency>3</dependency>
  </node>
  <node id="5" type="output">
    <instruction>Return the final answer derived from the verified calculation.</instruction>
    <dependency>4</dependency>
  </node>