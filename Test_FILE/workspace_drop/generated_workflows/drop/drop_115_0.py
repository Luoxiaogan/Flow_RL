# Workflow ID: drop_115_0
# Benchmark: drop
# Data Indices: [3863, 1030, 3033, 3796, 1208]

<node id="1" type="input">
    <param name="problem" type="string"/>
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract relevant numerical data from the passage related to the question. Identify all instances of yardage for passes or distances mentioned.</instruction>
    <input>problem</input>
    <output>extracted_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>Filter and isolate only touchdown pass yardages from the extracted data. Ignore field goals, runs, or other non-passing plays.</instruction>
    <input>extracted_data</input>
    <output>touchdown_passes</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Determine the longest touchdown pass by comparing all values in the list of touchdown passes.</instruction>
    <input>touchdown_passes</input>
    <output>longest_pass</output>
  </node>
  
  <node id="5" type="agent">
    <instruction>Verify that the longest pass value is correctly identified and matches the expected format (integer in yards).</instruction>
    <input>longest_pass</input>
    <output>validated_result</output>
  </node>
  
  <node id="6" type="output">
    <input>validated_result</input>
  </node>