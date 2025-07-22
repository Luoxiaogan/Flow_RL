# Workflow ID: drop_866_0
# Benchmark: drop
# Data Indices: [3467, 231, 1365, 1181]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify key values and their context.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform the required arithmetic operation based on the extracted data. If comparing two quantities, subtract the smaller from the larger.</instruction>
    <input>2</input>
    <output>calculation_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the calculation by checking units, logic, and consistency with the passage. Ensure no misinterpretation occurred.</instruction>
    <input>3</input>
    <output>verification_result</output>
  </node>
  <node id="5" type="agent">
    <instruction>Format the final answer clearly as a number or short phrase that directly answers the question.</instruction>
    <input>4</input>
    <output>final_answer</output>
  </node>
  <node id="6" type="output">
    <parameter>final_answer</parameter>
  </node>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>
  <edge from="4" to="5"/>
  <edge from="5" to="6"/>