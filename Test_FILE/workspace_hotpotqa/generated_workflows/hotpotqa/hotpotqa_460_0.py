# Workflow ID: hotpotqa_460_0
# Benchmark: hotpotqa
# Data Indices: [779, 2747, 3451, 3896]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the key entities. Focus on direct relationships and attributes.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify the extracted information against the problem's specific query to ensure relevance and accuracy.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Check for any indirect connections or logical inferences that may be necessary to derive the final answer.</prompt>
  </node>
  <node id="5" type="agent">
    <prompt>Validate all steps by cross-referencing with known facts or multiple sources in the context.</prompt>
  </node>
  <node id="6" type="output">
    <prompt>Provide the final answer based on validated information, ensuring clarity and correctness.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>