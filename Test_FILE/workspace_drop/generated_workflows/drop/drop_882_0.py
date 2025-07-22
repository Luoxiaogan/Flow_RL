# Workflow ID: drop_882_0
# Benchmark: drop
# Data Indices: [3296, 2171, 695, 3442, 3980]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific values needed to answer the question based on the extracted data.</instruction>
    <input>2</input>
    <output>identified_values</output>
  </node>
  <node id="4" type="agent">
    <instruction>Perform necessary calculations or logical comparisons using the identified values.</instruction>
    <input>3</input>
    <output>calculation_result</output>
  </node>
  <node id="5" type="agent">
    <instruction>Validate the result against the context of the question to ensure accuracy.</instruction>
    <input>4</input>
    <output>validated_result</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
    <output>final_answer</output>
  </node>