# Workflow ID: drop_68_0
# Benchmark: drop
# Data Indices: [3813, 3406, 2821, 2984, 3148]

<node id="1" type="input">
    <param name="problem" />
  </node>
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage that could relate to the question.</instruction>
    <input>1</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Identify the key terms in the question (e.g., "years", "wins", "field goal") to match with extracted data.</instruction>
    <input>2</input>
    <output>key_terms</output>
  </node>
  <node id="4" type="agent">
    <instruction>Map the key terms to the extracted numerical data and determine which value answers the question.</instruction>
    <input>3</input>
    <output>mapped_value</output>
  </node>
  <node id="5" type="agent">
    <instruction>Validate the mapped value against the context of the question to ensure correctness.</instruction>
    <input>4</input>
    <output>validated_answer</output>
  </node>
  <node id="6" type="output">
    <input>5</input>
    <output>final_answer</output>
  </node>