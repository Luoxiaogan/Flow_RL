# Workflow ID: hotpotqa_288_0
# Benchmark: hotpotqa
# Data Indices: [3273, 2668, 2555, 1855, 2422]

<operator id="1" type="agent">
    <instruction>Identify the key entities and relationships in the context provided. Focus on the geographical features and their connections.</instruction>
  </operator>
  <operator id="2" type="agent">
    <instruction>From the context, determine which city is 18 miles east of Tybee Island based on the given geographical references.</instruction>
  </operator>
  <operator id="3" type="agent">
    <instruction>Verify that Lazaretto Creek divides Tybee Island from McQueens Island and confirm the location of Tybee Island relative to Georgia cities.</instruction>
  </operator>
  <operator id="4" type="agent">
    <instruction>Use the information that Tybee Island is 18 miles east of Savannah to deduce the answer.</instruction>
  </operator>
  <operator id="5" type="agent">
    <instruction>Combine all verified information to produce the final answer: the Georgia city located 18 miles west of Tybee Island.</instruction>
  </operator>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="4"/>
  <connection from="4" to="5"/>