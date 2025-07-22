# Workflow ID: hotpotqa_37_0
# Benchmark: hotpotqa
# Data Indices: [577, 2617, 3142, 792, 3143]

<operator id="1">
    <instruction>Identify the key elements in the question and map them to relevant context information.</instruction>
    <input>problem</input>
    <output>key_elements</output>
  </operator>
  <operator id="2">
    <instruction>Extract specific details from the context that directly answer the question.</instruction>
    <input>key_elements, context</input>
    <output>relevant_details</output>
  </operator>
  <operator id="3">
    <instruction>Validate if the extracted details form a coherent and correct answer.</instruction>
    <input>relevant_details</input>
    <output>validated_answer</output>
  </operator>
  <operator id="4">
    <instruction>Format the validated answer into a concise and clear response.</instruction>
    <input>validated_answer</input>
    <output>final_answer</output>
  </operator>
  <link from="1" to="2"/>
  <link from="2" to="3"/>
  <link from="3" to="4"/>