# Workflow ID: drop_883_0
# Benchmark: drop
# Data Indices: [474, 322, 194, 476]

<node id="1" type="input">
    <data>problem</data>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical values and categories in the problem. Determine what is being compared or asked.</instruction>
    <input>1</input>
  </node>
  <node id="3" type="agent">
    <instruction>Extract relevant data points that directly answer the question. Ignore extraneous information.</instruction>
    <input>2</input>
  </node>
  <node id="4" type="agent">
    <instruction>Compare the extracted values logically to determine which is larger, smaller, or the difference between them.</instruction>
    <input>3</input>
  </node>
  <node id="5" type="agent">
    <instruction>Verify the conclusion by cross-checking with the original passage for accuracy.</instruction>
    <input>4</input>
  </node>
  <node id="6" type="output">
    <input>5</input>
  </node>