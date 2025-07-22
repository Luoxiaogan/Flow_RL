# Workflow ID: hotpotqa_116_0
# Benchmark: hotpotqa
# Data Indices: [113, 1509, 2344, 2811]

<operator id="0">
    <instruction>Identify the key entities and relationships in the input context to determine the correct answer.</instruction>
    <input>context</input>
    <output>entity_list</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant information from the entity list that directly answers the question.</instruction>
    <input>entity_list</input>
    <output>relevant_info</output>
  </operator>
  <operator id="2">
    <instruction>Validate the extracted information against known facts or timelines to ensure accuracy.</instruction>
    <input>relevant_info</input>
    <output>validated_answer</output>
  </operator>
  <operator id="3">
    <instruction>Format the validated answer into a clear, concise response suitable for the given question.</instruction>
    <input>validated_answer</input>
    <output>final_output</output>
  </operator>