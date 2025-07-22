# Workflow ID: hotpotqa_382_0
# Benchmark: hotpotqa
# Data Indices: [306, 1940, 3396, 3382, 876]

<operator id="1">
    <instruction>Identify the key entities in the context relevant to the question. Break down the problem into its core components.</instruction>
    <input>context, question</input>
    <output>entities, components</output>
  </operator>
  
  <operator id="2">
    <instruction>For each entity, determine whether it directly answers or relates to the question. Filter out irrelevant information.</instruction>
    <input>entities, components, question</input>
    <output>relevant_entities</output>
  </operator>
  
  <operator id="3">
    <instruction>Extract specific values or facts from the relevant entities that can answer the question directly.</instruction>
    <input>relevant_entities, question</input>
    <output>candidate_answers</output>
  </operator>
  
  <operator id="4">
    <instruction>Validate candidate answers against the original question. Eliminate any that do not fully satisfy the query.</instruction>
    <input>candidate_answers, question</input>
    <output>valid_answers</output>
  </operator>
  
  <operator id="5">
    <instruction>Among the valid answers, select the one that is most precise and unambiguous based on the context.</instruction>
    <input>valid_answers</input>
    <output>final_answer</output>
  </operator>