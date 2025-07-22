# Workflow ID: hotpotqa_553_0
# Benchmark: hotpotqa
# Data Indices: [1491, 1045, 3751, 956, 2081]

<operator id="0">
    <instruction>Identify the key entities in the problem and their relationships. Focus on the main subject, the associated group or category, and any relevant connections.</instruction>
    <input>problem</input>
    <output>entity_analysis</output>
  </operator>
  <operator id="1">
    <instruction>Based on the entity analysis, determine which agent or entity is directly linked to the question's focus. Ensure this step isolates the correct subject for further investigation.</instruction>
    <input>entity_analysis</input>
    <output>subject_identification</output>
  </operator>
  <operator id="2">
    <instruction>Extract all contextual clues that may help verify or clarify the relationship between the subject and the answer. Prioritize information that supports a direct link to the solution.</instruction>
    <input>subject_identification</input>
    <output>context_clues</output>
  </operator>
  <operator id="3">
    <instruction>Use the context clues to deduce the final answer. Apply logical reasoning to eliminate irrelevant options and confirm the correct response based on the evidence.</instruction>
    <input>context_clues</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>