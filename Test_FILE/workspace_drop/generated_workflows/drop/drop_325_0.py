# Workflow ID: drop_325_0
# Benchmark: drop
# Data Indices: [1233, 755, 2553, 1754]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Identify the key numerical or percentage data in the passage related to the question. Focus on extracting exact values and their context.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Apply the relevant mathematical operation (e.g., subtraction, percentage calculation) using the extracted data to answer the question step by step.</instruction>
    <input>extracted_data</input>
    <output>calculated_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the calculated result matches the question's requirement—ensure units, precision, and logic are correct.</instruction>
    <input>calculated_result</input>
    <output>final_answer</output>
  </node>
  <node id="5" type="output">
    <param name="answer" value="final_answer" />
  </node>
  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />
  <edge from="4" to="5" />