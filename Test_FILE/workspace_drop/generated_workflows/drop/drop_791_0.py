# Workflow ID: drop_791_0
# Benchmark: drop
# Data Indices: [1932, 545, 789, 371, 2105]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract key numerical data from the passage relevant to the question. Focus on identifying all values that could contribute to the answer.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific relationship or operation needed to compute the final answer based on the extracted data. Think step by step: what must be calculated or compared?</instruction>
    <input>2</input>
    <output>calculation_logic</output>
  </node>
  <node id="4" type="agent">
    <instruction>Apply the calculation logic to the extracted data to produce a precise result. Ensure accuracy and avoid unnecessary steps.</instruction>
    <input>3</input>
    <output>final_answer</output>
  </node>
  <node id="5" type="agent">
    <instruction>Verify the correctness of the final answer by cross-checking with the original passage. Confirm it aligns with the question asked.</instruction>
    <input>4</input>
    <output>verification_result</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
    <output>final_answer</output>
  </node>