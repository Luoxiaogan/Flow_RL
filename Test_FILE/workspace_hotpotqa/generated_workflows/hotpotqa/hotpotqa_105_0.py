# Workflow ID: hotpotqa_105_0
# Benchmark: hotpotqa
# Data Indices: [957, 134, 1034, 3049, 1027]

<node id="1" type="input">
    <prompt>Understand the question and extract key entities.</prompt>
  </node>
  <node id="2" type="agent">
    <prompt>Identify the main subject and relevant context for the question. Think step by step to isolate the correct answer from the provided context.</prompt>
  </node>
  <node id="3" type="agent">
    <prompt>Verify if the extracted entities match known facts or roles in the given context. Ensure no ambiguity remains.</prompt>
  </node>
  <node id="4" type="agent">
    <prompt>Check for direct associations between the entities and the required answer (e.g., film roles, publications, etc.).</prompt>
  </node>
  <node id="5" type="output">
    <prompt>Return the final answer based on the validated information from previous steps.</prompt>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>