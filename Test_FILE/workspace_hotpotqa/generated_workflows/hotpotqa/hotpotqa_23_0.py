# Workflow ID: hotpotqa_23_0
# Benchmark: hotpotqa
# Data Indices: [992, 176, 1340, 2364, 213]

<node id="1" type="input">
    <prompt>Understand the question and identify key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Extract relevant information from context related to the question. Focus on direct mentions of the entity or concept in question.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify that the extracted information directly answers the question. If not, look for indirect connections or additional context.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Ensure no irrelevant details are included—only what is necessary to answer the question correctly.</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on verified information. Make sure it is precise and matches the question format.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>