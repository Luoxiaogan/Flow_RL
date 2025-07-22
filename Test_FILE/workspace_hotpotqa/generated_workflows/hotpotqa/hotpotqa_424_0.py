# Workflow ID: hotpotqa_424_0
# Benchmark: hotpotqa
# Data Indices: [2599, 3976, 3702, 3951, 3406]

<operator id="1">
    <instruction>Identify the key entities and relationships in the problem context.</instruction>
    <input>problem</input>
    <output>entity_list</output>
  </operator>
  
  <operator id="2">
    <instruction>Extract specific roles or titles associated with each entity that matches the question.</instruction>
    <input>entity_list</input>
    <output>role_mapping</output>
  </operator>
  
  <operator id="3">
    <instruction>Filter for agents whose roles match the question's criteria (e.g., writer, producer, and a third role).</instruction>
    <input>role_mapping</input>
    <output>qualified_agents</output>
  </operator>
  
  <operator id="4">
    <instruction>For each qualified agent, determine the missing role based on their known roles and common industry positions.</instruction>
    <input>qualified_agents</input>
    <output>missing_roles</output>
  </operator>
  
  <operator id="5">
    <instruction>Aggregate the results to identify the consistent third role across all matching agents.</instruction>
    <input>missing_roles</input>
    <output>final_answer</output>
  </operator>