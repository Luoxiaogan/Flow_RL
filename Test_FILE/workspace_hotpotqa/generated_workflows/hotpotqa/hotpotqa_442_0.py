# Workflow ID: hotpotqa_442_0
# Benchmark: hotpotqa
# Data Indices: [2158, 2425, 456, 1811, 1081]

<operator id="1" type="agent">
    <instruction>Identify the key entity in the question and locate its relevant context.</instruction>
    <input>problem</input>
    <output>entity_context</output>
  </operator>
  
  <operator id="2" type="agent">
    <instruction>Extract the core information from the context that directly answers the question.</instruction>
    <input>entity_context</input>
    <output>extracted_info</output>
  </operator>
  
  <operator id="3" type="agent">
    <instruction>Verify the extracted information against known facts or logical consistency to ensure accuracy.</instruction>
    <input>extracted_info</input>
    <output>verified_answer</output>
  </operator>
  
  <operator id="4" type="agent">
    <instruction>Format the verified answer into a clear, concise response suitable for direct output.</instruction>
    <input>verified_answer</input>
    <output>final_output</output>
  </operator>
  
  <operator id="5" type="agent">
    <instruction>Check if the final output aligns with the original question and satisfies all required criteria.</instruction>
    <input>final_output</input>
    <output>validation_result</output>
  </operator>
  
  <operator id="6" type="agent">
    <instruction>Generate a summary of the reasoning steps taken to arrive at the final answer.</instruction>
    <input>entity_context, extracted_info, verified_answer</input>
    <output>reasoning_summary</output>
  </operator>
  
  <operator id="7" type="agent">
    <instruction>Ensure no problem-specific details are leaked in the final graph structure; confirm compliance with privacy constraints.</instruction>
    <input>graph_structure</input>
    <output>compliance_check</output>
  </operator>
  
  <operator id="8" type="agent">
    <instruction>Finalize the optimized graph by removing redundant nodes and ensuring clarity and correctness.</instruction>
    <input>validated_graph</input>
    <output>optimized_graph</output>
  </operator>