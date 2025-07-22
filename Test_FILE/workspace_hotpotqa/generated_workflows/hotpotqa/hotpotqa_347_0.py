# Workflow ID: hotpotqa_347_0
# Benchmark: hotpotqa
# Data Indices: [1164, 1740, 3938, 499]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the key entities. Focus on one entity at a time.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted information directly answers the question or supports the final answer.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Combine results from previous agents into a coherent response, ensuring no contradictions.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on validated information.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>