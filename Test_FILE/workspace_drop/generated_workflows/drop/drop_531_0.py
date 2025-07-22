# Workflow ID: drop_531_0
# Benchmark: drop
# Data Indices: [2028, 1645, 181, 3243, 2782]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <dependency>1</dependency>
  </node>
  <node id="3" type="agent">
    <instruction>Compare the extracted values to determine the answer to the question.</instruction>
    <dependency>2</dependency>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the correctness of the comparison by cross-checking with the passage context.</instruction>
    <dependency>3</dependency>
  </node>
  <node id="5" type="output">
    <instruction>Return the final answer based on the verified comparison.</instruction>
    <dependency>4</dependency>
  </node>