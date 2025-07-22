# Workflow ID: drop_226_0
# Benchmark: drop
# Data Indices: [3120, 3511, 980, 3220]

<operator id="1">
    <instruction>Extract relevant numerical data from the passage that pertains to the question.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </operator>

  <operator id="2">
    <instruction>Identify the mathematical operation needed to answer the question based on the extracted data.</instruction>
    <input>extracted_data</input>
    <output>operation</output>
  </operator>

  <operator id="3">
    <instruction>Perform the calculation using the identified operation and input values.</instruction>
    <input>operation, extracted_data</input>
    <output>result</output>
  </operator>

  <operator id="4">
    <instruction>Validate the result by cross-checking with the original passage for consistency.</instruction>
    <input>result, problem</input>
    <output>validated_result</output>
  </operator>

  <operator id="5">
    <instruction>Format the final answer in a clear and concise manner suitable for the question asked.</instruction>
    <input>validated_result</input>
    <output>final_answer</output>
  </operator>

  <operator id="6">
    <instruction>Ensure all operators have contributed meaningfully to the final output; if not, refine the graph accordingly.</instruction>
    <input>final_answer</input>
    <output>optimized_graph</output>
  </operator>