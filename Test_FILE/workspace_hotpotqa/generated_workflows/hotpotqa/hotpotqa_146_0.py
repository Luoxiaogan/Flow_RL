# Workflow ID: hotpotqa_146_0
# Benchmark: hotpotqa
# Data Indices: [2286, 829, 1032, 307, 1258]

<agent id="1">
    <instruction>Identify the key entities and relationships in the context relevant to the question. Focus on extracting structured information that directly answers the query.</instruction>
    <input>problem</input>
    <output>structured_data</output>
  </agent>
  
  <agent id="2">
    <instruction>Process the structured data to locate the specific answer by matching keywords, names, or events mentioned in the question.</instruction>
    <input>structured_data</input>
    <output>candidate_answer</output>
  </agent>
  
  <agent id="3">
    <instruction>Validate the candidate answer against all available context to ensure accuracy and eliminate false positives from similar-sounding names or unrelated facts.</instruction>
    <input>candidate_answer</input>
    <input>context</input>
    <output>validated_answer</output>
  </agent>
  
  <agent id="4">
    <instruction>Format the validated answer into a concise, clear response that directly addresses the original question without extra explanation.</instruction>
    <input>validated_answer</input>
    <output>final_answer</output>
  </agent>
  
  <connect from="1" to="2"/>
  <connect from="2" to="3"/>
  <connect from="3" to="4"/>