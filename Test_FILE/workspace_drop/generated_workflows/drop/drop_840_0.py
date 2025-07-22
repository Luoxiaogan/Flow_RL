# Workflow ID: drop_840_0
# Benchmark: drop
# Data Indices: [3385, 1429, 256, 3312, 3412]

<node id="1" type="input">
    <param name="problem" />
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify all scores, points, or counts mentioned that could contribute to answering the question.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Parse the extracted data to isolate values directly tied to the question's subject (e.g., touchdowns by position, field goals per half). Apply logical grouping based on the question's focus.</instruction>
    <input>extracted_data</input>
    <output>grouped_values</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Perform arithmetic operations (e.g., subtraction, comparison) between the grouped values to compute the difference asked in the question. Ensure units and categories match.</instruction>
    <input>grouped_values</input>
    <output>computed_result</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>Validate the computed result against the passage context to ensure no misinterpretation of roles (e.g., distinguishing wide receivers vs tight ends). Confirm correctness before finalizing.</instruction>
    <input>computed_result</input>
    <input>problem</input>
    <output>final_answer</output>
  </node>
  
  <node id="6" type="output">
    <input>final_answer</input>
  </node>