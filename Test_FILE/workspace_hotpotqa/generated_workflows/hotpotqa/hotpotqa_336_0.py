# Workflow ID: hotpotqa_336_0
# Benchmark: hotpotqa
# Data Indices: [281, 2442, 3463, 3947]

<operator id="0">
    <instruction>Identify the key entities in the problem context that are directly related to the question.</instruction>
    <input>problem</input>
    <output>entities</output>
  </operator>
  <operator id="1">
    <instruction>Extract specific details from the context that link the identified entities to the answer.</instruction>
    <input>entities</input>
    <output>linked_details</output>
  </operator>
  <operator id="2">
    <instruction>Verify if the linked details contain a direct or indirect match to the question's requirement.</instruction>
    <input>linked_details</input>
    <output>match_found</output>
  </operator>
  <operator id="3">
    <instruction>If a match is found, return the relevant information as the final answer. Otherwise, indicate no clear answer exists.</instruction>
    <input>match_found</input>
    <output>final_answer</output>
  </operator>
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>