# Workflow ID: hotpotqa_269_0
# Benchmark: hotpotqa
# Data Indices: [510, 2708, 2424, 3071]

<agent id="1">
    <instruction>Identify the key entities and relationships in the problem statement. Focus on extracting the relevant information needed to solve the question.</instruction>
    <input>problem</input>
    <output>entity_list, relationship_graph</output>
  </agent>
  <agent id="2">
    <instruction>Filter and refine the extracted entities based on relevance to the specific question being asked. Eliminate any irrelevant data that does not contribute to the final answer.</instruction>
    <input>entity_list, relationship_graph</input>
    <output>filtered_entities</output>
  </agent>
  <agent id="3">
    <instruction>Use logical deduction to determine which entity or value directly answers the question. If multiple values are present, identify the one that satisfies all constraints of the question.</instruction>
    <input>filtered_entities</input>
    <output>candidate_answer</output>
  </agent>
  <agent id="4">
    <instruction>Validate the candidate answer by cross-referencing with the context provided. Ensure that no conflicting information exists and that the answer is fully supported by the input data.</instruction>
    <input>candidate_answer, context</input>
    <output>final_answer</output>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>