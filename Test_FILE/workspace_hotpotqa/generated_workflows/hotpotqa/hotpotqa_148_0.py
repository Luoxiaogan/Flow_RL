# Workflow ID: hotpotqa_148_0
# Benchmark: hotpotqa
# Data Indices: [2568, 3759, 2037, 339]

<node id="1" type="input">
    <prompt>Understand the question and extract key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify relevant context for the key entities in the question.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Verify if the extracted information directly answers the question or requires further reasoning.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Apply logical inference to derive the correct answer from verified information.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the derived logic.</prompt>
    <depends_on>4</depends_on>
  </node>