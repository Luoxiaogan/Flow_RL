# Workflow ID: hotpotqa_294_0
# Benchmark: hotpotqa
# Data Indices: [3425, 3228, 768, 3547, 3356]

<agent id="1" type="reasoning">
    <instruction>Identify the key entities in the question and determine what information is needed to answer it.</instruction>
    <input>problem</input>
    <output>Extracted entities: "Christine Harper", "company", "headquartered at 1585 Broadway"</output>
  </agent>
  
  <agent id="2" type="search">
    <instruction>Find which company is headquartered at 1585 Broadway based on context clues.</instruction>
    <input>1585 Broadway</input>
    <output>Morgan Stanley Building, headquarters of Morgan Stanley</output>
  </agent>
  
  <agent id="3" type="verify">
    <instruction>Confirm that Christine Harper covers this company based on the provided context.</instruction>
    <input>Christine Harper, Morgan Stanley</input>
    <output>Christine Harper is a chief financial correspondent for Bloomberg News who has reported on Morgan Stanley since 2006.</output>
  </agent>
  
  <agent id="4" type="synthesize">
    <instruction>Combine the results from previous agents to produce the final answer.</instruction>
    <input>2, 3</input>
    <output>Morgan Stanley</output>
  </agent>
  
  <edge from="1" to="2" />
  <edge from="2" to="3" />
  <edge from="3" to="4" />