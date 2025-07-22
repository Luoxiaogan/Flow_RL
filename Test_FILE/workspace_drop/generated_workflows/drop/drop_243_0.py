# Workflow ID: drop_243_0
# Benchmark: drop
# Data Indices: [499, 1820, 1658, 1354]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract all relevant numerical data from the passage related to the question. Identify key events such as touchdowns, field goals, and their distances.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific values mentioned in the question (e.g., touchdown runs by certain players) and locate them in the extracted data. Perform necessary comparisons or calculations.</instruction>
    <input>extracted_data</input>
    <output>calculated_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the correctness of the calculated result by cross-referencing with the original passage. Ensure no misinterpretation occurred.</instruction>
    <input>calculated_result, problem</input>
    <output>verified_result</output>
  </node>
  <node id="5" type="output">
    <input>verified_result</input>
  </node>