# Workflow ID: hotpotqa_131_0
# Benchmark: hotpotqa
# Data Indices: [163, 1447, 428, 1383]

<operator id="0">
    <instruction>Understand the core question and identify key entities mentioned.</instruction>
    <input>problem</input>
    <output>key_entities</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant information from context related to each key entity.</instruction>
    <input>key_entities</input>
    <output>extracted_info</output>
  </operator>
  <operator id="2">
    <instruction>Filter and validate information that directly answers the question.</instruction>
    <input>extracted_info</input>
    <output>validated_answer</output>
  </operator>
  <operator id="3">
    <instruction>Ensure all steps logically connect and contribute to final answer.</instruction>
    <input>validated_answer</output>
    <output>final_output</output>
  </operator>