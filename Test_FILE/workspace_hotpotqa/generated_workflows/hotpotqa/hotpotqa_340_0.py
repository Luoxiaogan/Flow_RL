# Workflow ID: hotpotqa_340_0
# Benchmark: hotpotqa
# Data Indices: [705, 3878, 528, 2816]

<operator id="1" type="reasoning">
    <instruction>Identify the key elements in the question and determine what information is needed to answer it.</instruction>
    <input>question</input>
    <output>key_elements</output>
  </operator>
  
  <operator id="2" type="retrieval">
    <instruction>Find the relevant context that contains the answer to the key elements identified in operator 1.</instruction>
    <input>key_elements, context</input>
    <output>relevant_context</output>
  </operator>
  
  <operator id="3" type="analysis">
    <instruction>Extract the specific detail from the relevant context that directly answers the question.</instruction>
    <input>relevant_context</input>
    <output>answer_detail</output>
  </operator>
  
  <operator id="4" type="verification">
    <instruction>Verify that the extracted detail matches the question and is unambiguous.</instruction>
    <input>answer_detail, question</input>
    <output>verified_answer</output>
  </operator>
  
  <operator id="5" type="formatting">
    <instruction>Format the verified answer into a clear, concise response suitable for the user.</instruction>
    <input>verified_answer</input>
    <output>final_answer</output>
  </operator>