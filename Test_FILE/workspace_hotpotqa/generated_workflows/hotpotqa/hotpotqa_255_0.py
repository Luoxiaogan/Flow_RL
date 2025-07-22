# Workflow ID: hotpotqa_255_0
# Benchmark: hotpotqa
# Data Indices: [2014, 1572, 392, 2153]

<operator id="0">
    <instruction>Think step by step to identify the key elements in the question and context that directly relate to the answer.</instruction>
    <input>problem</input>
    <output>step1_analysis</output>
  </operator>
  <operator id="1">
    <instruction>Extract relevant entities from the context that match the criteria in the question, such as names, dates, or specific works.</instruction>
    <input>step1_analysis</input>
    <output>step2_entities</output>
  </operator>
  <operator id="2">
    <instruction>Filter the extracted entities to narrow down to the one that precisely answers the question.</instruction>
    <input>step2_entities</input>
    <output>step3_filtered</output>
  </operator>
  <operator id="3">
    <instruction>Validate the filtered result against the question's requirements to ensure accuracy and completeness.</instruction>
    <input>step3_filtered</input>
    <output>final_answer</output>
  </operator>
  <operator id="4">
    <instruction>Double-check the final answer using alternative context clues to prevent errors due to ambiguous information.</instruction>
    <input>final_answer</input>
    <output>validated_answer</output>
  </operator>
  <operator id="5">
    <instruction>Return the validated answer only if it matches all criteria; otherwise, return an error message indicating missing information.</instruction>
    <input>validated_answer</input>
    <output>result</output>
  </operator>