# Workflow ID: drop_331_0
# Benchmark: drop
# Data Indices: [3450, 1950, 1707, 1052, 1263]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant information from the passage that directly answers the question. Focus on key entities, numbers, and events mentioned.</instruction>
    <input>problem</input>
    <output>extracted_info</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific part of the extracted information that corresponds to the question being asked. If multiple pieces of data are present, determine which one is most relevant.</instruction>
    <input>extracted_info</input>
    <output>relevant_data</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the relevant data matches the format required by the question (e.g., number, name, time period). If it does not, re-examine the passage for clarification.</instruction>
    <input>relevant_data</input>
    <output>validated_answer</output>
  </node>
  <node id="5" type="output">
    <input>validated_answer</input>
  </node>