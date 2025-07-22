# Workflow ID: hotpotqa_74_0
# Benchmark: hotpotqa
# Data Indices: [1757, 1916, 2126, 3581]

<operator id="0">
    <instruction>Identify the key entities and relationships in the problem context to determine the relevant information for solving the question.</instruction>
    <input>problem</input>
    <output>filtered_context</output>
  </operator>
  <operator id="1">
    <instruction>Extract specific details about the subject mentioned in the question from the filtered context. Focus on distinguishing features or attributes that uniquely identify the subject.</instruction>
    <input>filtered_context</input>
    <output>candidate_entities</output>
  </operator>
  <operator id="2">
    <instruction>Compare each candidate entity against the criteria specified in the question to determine which one satisfies all conditions.</instruction>
    <input>candidate_entities</input>
    <output>matching_entity</output>
  </operator>
  <operator id="3">
    <instruction>Verify the correctness of the matching entity by cross-referencing with additional context details to ensure no ambiguity or misinterpretation.</instruction>
    <input>matching_entity, filtered_context</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>