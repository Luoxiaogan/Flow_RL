# Workflow ID: hotpotqa_276_0
# Benchmark: hotpotqa
# Data Indices: [1055, 647, 2865, 2161, 2679]

<operator id="0" type="agent">
    <instruction>Identify the key entities and relationships in the problem statement. Break down the question into its core components to determine what information is needed to answer it.</instruction>
    <input>problem</input>
    <output>analysis</output>
  </operator>
  
  <operator id="1" type="agent">
    <instruction>Based on the analysis, locate the relevant context that directly addresses the question. Filter out any extraneous or unrelated information.</instruction>
    <input>analysis, context</input>
    <output>relevant_context</output>
  </operator>
  
  <operator id="2" type="agent">
    <instruction>Extract the precise answer from the relevant context. Ensure the answer is unambiguous and matches the exact phrasing of the question.</instruction>
    <input>relevant_context</input>
    <output>answer</output>
  </operator>
  
  <operator id="3" type="agent">
    <instruction>Verify the answer by cross-referencing with other parts of the context to ensure accuracy and consistency.</instruction>
    <input>answer, context</input>
    <output>verification</output>
  </operator>
  
  <operator id="4" type="agent">
    <instruction>Finalize the response. If verification passes, return the answer. If not, flag for re-evaluation.</instruction>
    <input>verification</input>
    <output>final_answer</output>
  </operator>
  
  <connection from="0" to="1"/>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>