# Workflow ID: drop_790_0
# Benchmark: drop
# Data Indices: [1511, 571, 981, 569, 1403]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that answers the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Compare values in extracted_data to determine the correct answer based on the question's logic.</instruction>
    <input>2</input>
    <output>comparison_result</output>
  </node>
  <node id="4" type="agent">
    <instruction>Validate the comparison result against the passage context to ensure accuracy.</instruction>
    <input>3</input>
    <output>validated_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>