# Workflow ID: hotpotqa_398_0
# Benchmark: hotpotqa
# Data Indices: [3667, 3194, 2052, 1259, 260]

<agent id="1">
    <instruction>Identify the key entities mentioned in the context that relate to the question. Focus on extracting only the relevant information needed to answer the question.</instruction>
    <input>problem</input>
    <output>entity_list</output>
  </agent>
  
  <agent id="2">
    <instruction>For each entity, determine whether it is directly tied to the year of release. If so, extract the year. If not, discard it.</instruction>
    <input>entity_list</input>
    <output>year_candidates</output>
  </agent>
  
  <agent id="3">
    <instruction>Compare the extracted years from all candidates. If there is a consistent year across multiple sources or entities, confirm it as the correct answer. If not, identify which entity is most authoritative for this question.</instruction>
    <input>year_candidates</input>
    <output>final_year</output>
  </agent>
  
  <agent id="4">
    <instruction>Verify the final year against known facts or cross-reference with external knowledge (if applicable). Ensure no conflicting data exists.</instruction>
    <input>final_year</input>
    <output>verified_year</output>
  </agent>
  
  <agent id="5">
    <instruction>Return the verified year as the final answer. Do not include any extra text or explanation unless explicitly requested.</instruction>
    <input>verified_year</input>
    <output>answer</output>
  </agent>