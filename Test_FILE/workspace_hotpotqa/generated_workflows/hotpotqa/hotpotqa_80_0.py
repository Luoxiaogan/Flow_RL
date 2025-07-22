# Workflow ID: hotpotqa_80_0
# Benchmark: hotpotqa
# Data Indices: [2809, 2337, 1722, 1242, 1168]

<operator id="0" type="question_analysis">
    <input>problem</input>
    <output>analyzed_question</output>
    <instruction>Break down the question step by step to identify the key entities and relationships needed for solving.</instruction>
  </operator>
  
  <operator id="1" type="context_retrieval">
    <input>analyzed_question</input>
    <output>relevant_context</output>
    <instruction>Extract only the most relevant context snippets that directly relate to the entities in the question.</instruction>
  </operator>
  
  <operator id="2" type="entity_resolution">
    <input>relevant_context</input>
    <output>resolved_entities</output>
    <instruction>Identify and disambiguate key entities (e.g., people, places, companies) from the retrieved context.</instruction>
  </operator>
  
  <operator id="3" type="reasoning">
    <input>resolved_entities</input>
    <output>logical_chain</output>
    <instruction>Construct a step-by-step logical chain using the resolved entities to answer the question.</instruction>
  </operator>
  
  <operator id="4" type="answer_generation">
    <input>logical_chain</input>
    <output>final_answer</output>
    <instruction>Generate the final concise answer based on the logical chain.</instruction>
  </operator>
  
  <operator id="5" type="validation">
    <input>final_answer</input>
    <output>is_valid</output>
    <instruction>Verify the final answer matches the question's intent and is supported by the reasoning chain.</instruction>
  </operator>