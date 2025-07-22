# Workflow ID: hotpotqa_588_0
# Benchmark: hotpotqa
# Data Indices: [1000, 1254, 1899, 1915, 2450]

<node id="1" type="input">
    <prompt>Understand the core question and identify key entities mentioned.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the key entities. Focus on one entity at a time.</prompt>
    <depends_on>1</depends_on>
  </node>
  <node id="3" type="agent">
    <prompt>Verify if the extracted information directly answers the question or requires further connection.</prompt>
    <depends_on>2</depends_on>
  </node>
  <node id="4" type="agent">
    <prompt>Identify any missing links between entities that must be resolved to form a complete answer.</prompt>
    <depends_on>3</depends_on>
  </node>
  <node id="5" type="agent">
    <prompt>Construct a logical chain connecting all verified pieces of evidence to derive the final answer.</prompt>
    <depends_on>4</depends_on>
  </node>
  <node id="6" type="output">
    <prompt>Return the final, logically derived answer based on the chain of reasoning.</prompt>
    <depends_on>5</depends_on>
  </node>