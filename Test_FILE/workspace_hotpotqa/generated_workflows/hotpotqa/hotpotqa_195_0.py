# Workflow ID: hotpotqa_195_0
# Benchmark: hotpotqa
# Data Indices: [387, 3859, 2640, 1007, 1521]

<node id="1" type="input">
    <prompt>Understand the problem and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context for each entity mentioned in the question.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Verify if the extracted information directly answers the question or requires further processing.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Apply logical reasoning to connect the verified information to the final answer.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the processed information.</prompt>
    <depends_on>4</depends_on>
  </node>