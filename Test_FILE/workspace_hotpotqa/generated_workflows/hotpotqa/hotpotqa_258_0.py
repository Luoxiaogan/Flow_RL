# Workflow ID: hotpotqa_258_0
# Benchmark: hotpotqa
# Data Indices: [1578, 656, 1240, 1117, 2385]

<operator id="1" type="reasoning">
    <instruction>Think step by step to identify the core concept in the question and relevant context.</instruction>
    <input>problem</input>
    <output>core_concept</output>
  </operator>
  
  <operator id="2" type="retrieval">
    <instruction>Extract all entities and terms related to the core concept from the context.</instruction>
    <input>core_concept, context</input>
    <output>related_entities</output>
  </operator>
  
  <operator id="3" type="filter">
    <instruction>Filter out irrelevant entities; keep only those directly tied to the question's subject.</instruction>
    <input>related_entities</input>
    <output>filtered_entities</output>
  </operator>
  
  <operator id="4" type="mapping">
    <instruction>Map filtered entities to known historical movements or affiliations.</instruction>
    <input>filtered_entities</input>
    <output>affiliations</output>
  </operator>
  
  <operator id="5" type="validation">
    <instruction>Validate each mapping against authoritative definitions (e.g., Zionism = national movement for Jewish homeland).</instruction>
    <input>affiliations</input>
    <output>valid_affiliations</output>
  </operator>
  
  <operator id="6" type="selection">
    <instruction>Select the single correct affiliation that best matches the question's intent.</instruction>
    <input>valid_affiliations</input>
    <output>final_answer</output>
  </operator>