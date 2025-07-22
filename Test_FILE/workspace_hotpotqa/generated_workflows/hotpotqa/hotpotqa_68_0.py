# Workflow ID: hotpotqa_68_0
# Benchmark: hotpotqa
# Data Indices: [1743, 1359, 975, 1516, 154]

<operator id="0" type="extract">
    <instruction>Extract the key entities from the context that relate to the question. Focus on names, dates, and specific roles mentioned.</instruction>
  </operator>
  <operator id="1" type="filter">
    <instruction>Filter the extracted entities to include only those relevant to the footballer added during the 2012–13 season at FC Bayern Munich.</instruction>
  </operator>
  <operator id="2" type="resolve">
    <instruction>Determine the nationality of the filtered player by cross-referencing with known biographical data.</instruction>
  </operator>
  <operator id="3" type="validate">
    <instruction>Verify that the resolved nationality matches the criteria in the question: born in 1988 and joined Bayern Munich in 2012–13.</instruction>
  </operator>
  <operator id="4" type="combine">
    <instruction>Combine the validated result into a final answer string formatted as "Nationality of the footballer."</instruction>
  </operator>