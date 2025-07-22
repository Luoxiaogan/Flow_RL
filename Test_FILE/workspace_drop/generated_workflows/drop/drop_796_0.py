# Workflow ID: drop_796_0
# Benchmark: drop
# Data Indices: [411, 1350, 2872, 3868, 1656]

<operator id="0">
    <instruction>Identify the key entities and relationships in the input problem. Break down the question to determine what information is needed to answer it.</instruction>
    <input>problem</input>
    <output>structured_query</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant numerical or categorical data from the passage that directly answers the structured query. Focus only on the required information to avoid noise.</instruction>
    <input>structured_query, passage</input>
    <output>extracted_data</output>
  </operator>
  <operator id="2">
    <instruction>Validate the extracted data against the question's requirements. Ensure the answer is complete, accurate, and directly addresses the query without ambiguity.</instruction>
    <input>extracted_data, question</input>
    <output>validated_answer</output>
  </operator>
  <operator id="3">
    <instruction>Format the validated answer into a clear, concise response that matches the expected output type (e.g., number, string, list).</instruction>
    <input>validated_answer</input>
    <output>final_output</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>