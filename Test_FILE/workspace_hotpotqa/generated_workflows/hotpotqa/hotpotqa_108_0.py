# Workflow ID: hotpotqa_108_0
# Benchmark: hotpotqa
# Data Indices: [200, 2670, 390, 1944, 1603]

<node id="1" type="input">
    <prompt>Understand the problem statement and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context for each question.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Map extracted entities to answer the specific question.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Validate the answer against all provided context.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Return the final verified answer.</prompt>
    <depends_on>4</depends_on>
  </node>