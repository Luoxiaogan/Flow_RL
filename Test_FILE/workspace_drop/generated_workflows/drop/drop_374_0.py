# Workflow ID: drop_374_0
# Benchmark: drop
# Data Indices: [285, 3350, 3558, 1040, 3715]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that relates to the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific values or conditions mentioned in the question and map them to the extracted data.</instruction>
    <input>2</input>
    <output>mapped_values</output>
  </node>
  <node id="4" type="agent">
    <instruction>Apply mathematical operations or logical checks to determine the final answer based on the mapped values.</instruction>
    <input>3</input>
    <output>final_answer</output>
  </node>
  <node id="5" type="agent">
    <instruction>Validate the solution by cross-checking with the original passage to ensure accuracy.</instruction>
    <input>4</input>
    <output>validation_result</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
    <output>result</output>
  </node>