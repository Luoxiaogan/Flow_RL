# Workflow ID: drop_799_0
# Benchmark: drop
# Data Indices: [925, 2915, 2723, 2202]

<node id="1" type="input">
    <param name="problem">self.problem</param>
  </node>
  
  <node id="2" type="agent">
    <instruction>Extract key entities and numerical values from the passage. Identify all instances of touchdowns and their yardages.</instruction>
    <param name="input">1</param>
    <output>extracted_data</output>
  </node>
  
  <node id="3" type="agent">
    <instruction>From the extracted data, identify all touchdown plays and their corresponding yardages. Filter out non-touchdown events like field goals or penalties.</instruction>
    <param name="input">2</param>
    <output>touchdowns</output>
  </node>
  
  <node id="4" type="agent">
    <instruction>Among the identified touchdowns, determine which one has the highest yardage. Return this value as the longest touchdown.</instruction>
    <param name="input">3</param>
    <output>longest_touchdown_yards</output>
  </node>
  
  <node id="5" type="output">
    <param name="result">4</param>
  </node>