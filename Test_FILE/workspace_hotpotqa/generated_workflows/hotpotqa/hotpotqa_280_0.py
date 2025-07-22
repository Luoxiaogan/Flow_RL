# Workflow ID: hotpotqa_280_0
# Benchmark: hotpotqa
# Data Indices: [2357, 1647, 3847, 257, 3758]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the key entities.</prompt>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="agent">
    <prompt>Verify the extracted information matches the question's requirements.</prompt>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="agent">
    <prompt>Determine the final answer based on verified information.</prompt>
    <dependencies>3</dependencies>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer.</prompt>
    <dependencies>4</dependencies>
  </node>