# Workflow ID: hotpotqa_374_0
# Benchmark: hotpotqa
# Data Indices: [2341, 3646, 2064, 2009, 2995]

<node id="1" type="input">
    <prompt>Understand the core question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the question. Focus on direct matches and logical connections.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify the extracted information against known facts or cross-reference with other context elements.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Ensure all steps are logically connected and contribute to the final answer without redundancy.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final, concise answer based on verified information.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>