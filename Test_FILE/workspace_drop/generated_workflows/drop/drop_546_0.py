# Workflow ID: drop_546_0
# Benchmark: drop
# Data Indices: [3286, 1162, 1781, 1391, 856]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage based on the question. Identify key values such as scores, distances, years, or time periods mentioned in the context.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Perform step-by-step reasoning to compute the required answer using the extracted data. If multiple operations are needed (e.g., averaging, subtracting, counting), ensure each step is logically derived from the previous one.</instruction>
    <input>2</input>
    <output>reasoned_answer</output>
  </node>
  <node id="4" type="agent">
    <instruction>Verify the correctness of the computed result by cross-checking against the original passage and ensuring no arithmetic or logical errors occurred during processing.</instruction>
    <input>3</input>
    <output>verified_answer</output>
  </node>
  <node id="5" type="output">
    <input>4</input>
    <output>final_answer</output>
  </node>