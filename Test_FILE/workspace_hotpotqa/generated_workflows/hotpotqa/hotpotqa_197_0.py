# Workflow ID: hotpotqa_197_0
# Benchmark: hotpotqa
# Data Indices: [2387, 1800, 826, 2908]

<node id="1" type="input">
    <prompt>Understand the core question and identify key entities involved.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the key entities. Focus on one entity at a time to avoid confusion.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify connections between extracted entities—look for direct or indirect links that answer the question.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Eliminate irrelevant or conflicting information based on logical consistency with the question.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Reconstruct the answer by combining validated facts in a clear, step-by-step manner.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Provide the final answer based on the reconstructed logic chain.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>