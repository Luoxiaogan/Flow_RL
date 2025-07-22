# Workflow ID: drop_315_0
# Benchmark: drop
# Data Indices: [2743, 1698, 235, 1331]

<node id="1" type="input">
    <param>problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract the relevant numerical data from the passage that answers the question. Focus on identifying the key numbers and their context.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify which number in the extracted data directly answers the question. If multiple numbers are present, determine which one is relevant based on the question's context.</instruction>
    <input>extracted_data</input>
    <output>relevant_number</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify that the relevant number is correctly interpreted according to the question’s requirement (e.g., points, months, etc.). Ensure no misinterpretation of units or context occurs.</instruction>
    <input>relevant_number</input>
    <output>verified_answer</output>
  </node>
  <node id="5" type="output">
    <input>verified_answer</input>
  </node>