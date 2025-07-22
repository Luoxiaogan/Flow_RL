# Workflow ID: drop_466_0
# Benchmark: drop
# Data Indices: [1003, 3955, 1853, 3860]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify all values that could be used in calculations.</instruction>
    <input>problem</input>
    <output>extracted_values</output>
  </node>
  <node id="3" type="agent">
    <instruction>Apply mathematical operations (e.g., subtraction, percentage calculation) based on the extracted values and the specific question being asked.</instruction>
    <input>extracted_values</input>
    <output>calculated_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the result by cross-checking against the original passage to ensure no misinterpretation occurred.</instruction>
    <input>calculated_result</input>
    <input>problem</input>
    <output>verified_result</output>
  </node>
  <node id="5" type="output">
    <input>verified_result</input>
  </node>