# Workflow ID: hotpotqa_177_0
# Benchmark: hotpotqa
# Data Indices: [291, 3842, 1827, 3782]

<operator id="1">
    <instruction>Identify the key entities and relationships in the problem context to determine what information is needed to answer the question.</instruction>
    <input>problem</input>
    <output>key_entities_and_relationships</output>
  </operator>
  
  <operator id="2">
    <instruction>Extract specific data points relevant to the question from the provided context, focusing only on the necessary details.</instruction>
    <input>key_entities_and_relationships</input>
    <output>relevant_data_points</output>
  </operator>
  
  <operator id="3">
    <instruction>Validate the extracted data by cross-referencing with other parts of the context to ensure accuracy and completeness.</instruction>
    <input>relevant_data_points</input>
    <output>validated_data</output>
  </operator>
  
  <operator id="4">
    <instruction>Construct a concise and accurate answer based on the validated data, ensuring it directly addresses the question asked.</instruction>
    <input>validated_data</input>
    <output>final_answer</output>
  </operator>
  
  <operator id="5">
    <instruction>Review the final answer for clarity, correctness, and alignment with the original question to prevent misinterpretation or omission.</instruction>
    <input>final_answer</input>
    <output>verified_final_answer</output>
  </operator>