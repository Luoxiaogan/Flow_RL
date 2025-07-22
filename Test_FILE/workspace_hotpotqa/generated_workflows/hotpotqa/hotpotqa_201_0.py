# Workflow ID: hotpotqa_201_0
# Benchmark: hotpotqa
# Data Indices: [929, 1134, 979, 2840, 2429]

<operator id="0" type="agent">
    <instruction>Identify the key entities in the problem and determine the core question being asked.</instruction>
    <input>problem</input>
    <output>entity_analysis</output>
  </operator>
  
  <operator id="1" type="agent">
    <instruction>For each entity, locate relevant context that addresses the specific question. Focus on temporal or categorical data.</instruction>
    <input>entity_analysis</input>
    <output>context_extraction</output>
  </operator>
  
  <operator id="2" type="agent">
    <instruction>Compare the extracted information to answer the core question directly. If multiple entities are involved, ensure all are addressed.</instruction>
    <input>context_extraction</input>
    <output>final_answer</output>
  </operator>
  
  <operator id="3" type="agent">
    <instruction>Verify the correctness of the final answer by cross-checking against the original context to avoid misinterpretation.</instruction>
    <input>final_answer, context_extraction</input>
    <output>verification_result</output>
  </operator>
  
  <operator id="4" type="agent">
    <instruction>If verification fails, refine the analysis from step 1 based on the error and recompute; otherwise, return the verified result.</instruction>
    <input>verification_result, entity_analysis</input>
    <output>optimized_answer</output>
  </operator>
  
  <edge from="0" to="1"/>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>