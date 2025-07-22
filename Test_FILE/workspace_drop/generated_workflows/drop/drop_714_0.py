# Workflow ID: drop_714_0
# Benchmark: drop
# Data Indices: [1987, 3410, 659, 1097, 746]

<node id="1" type="input">
    <parameter>problem</parameter>
  </node>
  <node id="2" type="agent">
    <instruction>Extract all relevant numerical data from the passage related to the question. Identify key events, scores, and statistics mentioned.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  <node id="3" type="agent">
    <instruction>Filter the extracted data to focus only on values that directly answer the specific question. Ignore irrelevant details like player names or game context unless they affect the count or value.</instruction>
    <input>extracted_data</input>
    <output>filtered_data</output>
  </node>
  <node id="4" type="agent">
    <instruction>Apply logical reasoning to determine the correct answer based on the filtered data. For example, if counting touchdowns between 5 and 10 yards, check for any yardage in that range.</instruction>
    <input>filtered_data</input>
    <output>reasoned_answer</output>
  </node>
  <node id="5" type="agent">
    <instruction>Validate the reasoned answer by cross-checking against the original passage to ensure no misinterpretation occurred due to ambiguous phrasing or missing context.</instruction>
    <input>reasoned_answer</input>
    <input>problem</input>
    <output>validated_answer</output>
  </node>
  <node id="6" type="output">
    <input>validated_answer</input>
  </node>