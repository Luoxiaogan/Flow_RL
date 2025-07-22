# Workflow ID: hotpotqa_578_0
# Benchmark: hotpotqa
# Data Indices: [2108, 1868, 443, 2521]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant context for the key entities mentioned in the question.</prompt>
    <dependencies>1</dependencies>
  </node>
  <node id="3" type="agent">
    <prompt>Match the extracted context to the specific details required by the question.</prompt>
    <dependencies>2</dependencies>
  </node>
  <node id="4" type="agent">
    <prompt>Verify the match against all provided context to ensure accuracy.</prompt>
    <dependencies>3</dependencies>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on verified information.</prompt>
    <dependencies>4</dependencies>
  </node>