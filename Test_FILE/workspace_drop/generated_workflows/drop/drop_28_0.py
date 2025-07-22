# Workflow ID: drop_28_0
# Benchmark: drop
# Data Indices: [3801, 471, 3537, 2006]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify all quantities mentioned that could be compared or counted.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the specific values required to answer the question. Determine which numbers from the extracted data are directly relevant to the comparison or count in the question.</instruction>
    <input>2</input>
    <output>relevant_values</output>
  </node>
  <node id="4" type="agent">
    <instruction>Perform the necessary arithmetic operation (e.g., subtraction, addition, comparison) using the relevant values to compute the final answer.</instruction>
    <input>3</input>
    <output>computed_result</output>
  </node>
  <node id="5" type="agent">
    <instruction>Verify the computed result by cross-checking with the original passage to ensure accuracy and consistency with the context.</instruction>
    <input>4</input>
    <output>verified_result</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
    <output>final_answer</output>
  </node>