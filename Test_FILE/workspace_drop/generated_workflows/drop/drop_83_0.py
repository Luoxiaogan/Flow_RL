# Workflow ID: drop_83_0
# Benchmark: drop
# Data Indices: [2922, 1942, 1673, 164]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical information related to the question. Focus on extracting only the relevant data points that directly answer the query.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform a step-by-step calculation or logical deduction based on the extracted data. Ensure each step is clearly reasoned and builds toward the final answer.</instruction>
    <input>extracted_data</input>
    <output>calculated_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the correctness of the calculated result by cross-checking against the original passage. Ensure no misinterpretation occurred in prior steps.</instruction>
    <input>calculated_result</input>
    <input>problem</input>
    <output>verified_result</output>
  </node>
  <node id="5" type="output">
    <input>verified_result</input>
  </node>