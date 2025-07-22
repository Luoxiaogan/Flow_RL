# Workflow ID: hotpotqa_480_0
# Benchmark: hotpotqa
# Data Indices: [3555, 2553, 3516, 3354, 2641]

<operator id="1" type="agent">
    <instruction>Think step by step to identify the key elements in the problem context that directly relate to the question.</instruction>
    <input>problem</input>
    <output>identified_elements</output>
  </operator>
  <operator id="2" type="agent">
    <instruction>Extract only the relevant information from the identified elements that answers the specific question.</instruction>
    <input>identified_elements</input>
    <output>relevant_info</output>
  </operator>
  <operator id="3" type="agent">
    <instruction>Verify the relevance and correctness of the extracted information against the original problem context.</instruction>
    <input>relevant_info</input>
    <output>verified_answer</output>
  </operator>
  <operator id="4" type="agent">
    <instruction>Format the verified answer into a concise, clear response that directly addresses the question.</instruction>
    <input>verified_answer</input>
    <output>final_answer</output>
  </operator>
  <link from="1" to="2"/>
  <link from="2" to="3"/>
  <link from="3" to="4"/>