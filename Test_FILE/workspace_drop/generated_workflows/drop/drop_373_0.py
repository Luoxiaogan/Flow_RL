# Workflow ID: drop_373_0
# Benchmark: drop
# Data Indices: [402, 774, 714, 2802]

<operator id="1">
    <instruction>Identify all instances of touchdown passes in the passage. Extract the yardage for each pass.</instruction>
    <input>problem</input>
    <output>list_of_touchdown_passes</output>
  </operator>

  <operator id="2">
    <instruction>Sort the list of touchdown passes by yardage in descending order to find the longest ones.</instruction>
    <input>list_of_touchdown_passes</input>
    <output>sorted_passes</output>
  </operator>

  <operator id="3">
    <instruction>Take the first two entries from the sorted list to determine the top two longest touchdown passes.</instruction>
    <input>sorted_passes</input>
    <output>top_two_passes</output>
  </operator>

  <operator id="4">
    <instruction>Format the result as a string listing the top two longest touchdown passes with their yardages.</instruction>
    <input>top_two_passes</input>
    <output>final_answer</output>
  </operator>

  <connect>
    <from>1</from>
    <to>2</to>
  </connect>
  <connect>
    <from>2</from>
    <to>3</to>
  </connect>
  <connect>
    <from>3</from>
    <to>4</to>
  </connect>