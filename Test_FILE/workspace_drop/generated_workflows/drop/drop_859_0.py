# Workflow ID: drop_859_0
# Benchmark: drop
# Data Indices: [336, 2709, 1464, 198, 3292]

<operator id="1">
    <instruction>Identify the key elements in the problem that relate to the question. Focus on specific details like names, numbers, and events mentioned.</instruction>
    <input>problem</input>
    <output>key_elements</output>
  </operator>
  
  <operator id="2">
    <instruction>Extract numerical values or quantities directly relevant to the question from the key elements. Ignore any extraneous information.</instruction>
    <input>key_elements</input>
    <output>relevant_numbers</output>
  </operator>
  
  <operator id="3">
    <instruction>Compare all extracted numbers to determine which one answers the question based on context (e.g., longest field goal, most points, etc.).</instruction>
    <input>relevant_numbers</input>
    <output>answer_candidate</output>
  </operator>
  
  <operator id="4">
    <instruction>Verify the answer candidate against the original passage to ensure it matches the question's requirement exactly.</instruction>
    <input>answer_candidate</input>
    <output>final_answer</output>
  </operator>
  
  <operator id="5">
    <instruction>If multiple candidates exist, select the one that fits the question's scope best (e.g., "longest" implies maximum value).</instruction>
    <input>relevant_numbers</input>
    <output>best_candidate</output>
  </operator>
  
  <operator id="6">
    <instruction>Ensure the final answer is a single numeric value without units or explanations unless explicitly asked.</instruction>
    <input>final_answer</input>
    <output>clean_final_answer</output>
  </operator>
  
  <operator id="7">
    <instruction>Validate that no logical steps were skipped between the input and output; if not, reprocess using intermediate operators.</instruction>
    <input>clean_final_answer</input>
    <output>validated_output</output>
  </operator>