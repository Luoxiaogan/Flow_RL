# Workflow ID: hotpotqa_511_0
# Benchmark: hotpotqa
# Data Indices: [406, 2050, 663, 967]

<operator id="0">
    <instruction>Identify the key entities and relationships in the problem statement. Focus on extracting the main subject, attributes, and connections.</instruction>
    <input>problem</input>
    <output>extracted_entities</output>
  </operator>
  <operator id="1">
    <instruction>Map the extracted entities to known categories (e.g., person, team, country, year). Ensure clarity and correctness of classification.</instruction>
    <input>extracted_entities</input>
    <output>classified_entities</output>
  </operator>
  <operator id="2">
    <instruction>Use contextual clues from the provided context to resolve ambiguous references or link entities to specific outcomes.</instruction>
    <input>classified_entities</input>
    <output>resolved_references</output>
  </operator>
  <operator id="3">
    <instruction>Verify consistency between the resolved references and the question being asked. Ensure all relevant information is accounted for.</instruction>
    <input>resolved_references</input>
    <output>validated_solution</output>
  </operator>
  <operator id="4">
    <instruction>Generate a concise final answer based on the validated solution. Avoid unnecessary details; focus only on the required output.</instruction>
    <input>validated_solution</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>