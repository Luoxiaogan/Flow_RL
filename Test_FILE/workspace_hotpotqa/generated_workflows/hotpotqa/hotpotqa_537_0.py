# Workflow ID: hotpotqa_537_0
# Benchmark: hotpotqa
# Data Indices: [2436, 2930, 474, 2169, 103]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from the context for each key entity.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Verify if the extracted information directly answers the question.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>If not, refine search or cross-reference with other context elements.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="agent">
    <prompt>Construct a clear and concise answer based on verified data.</prompt>
    <depends_on>4</depends_on>
  </node>
  <node id="6" type="output">
    <prompt>Provide the final answer.</prompt>
    <depends_on>5</depends_on>
  </node>