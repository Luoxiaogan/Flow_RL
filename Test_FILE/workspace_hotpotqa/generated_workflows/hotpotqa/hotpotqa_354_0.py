# Workflow ID: hotpotqa_354_0
# Benchmark: hotpotqa
# Data Indices: [386, 789, 1706, 827, 2704]

<agent id="1">
    <instruction>Identify the key entities and relationships in the problem context.</instruction>
    <output>Extract relevant facts such as names, events, dates, and locations that may connect to the answer.</output>
  </agent>
  <agent id="2">
    <instruction>Map extracted entities to possible answers by cross-referencing with known data points.</instruction>
    <output>Link each entity to potential solutions based on contextual clues (e.g., "Saudi Arabia won its first medal in bowling" → links to a specific event).</output>
  </agent>
  <agent id="3">
    <instruction>Validate candidate answers against temporal and categorical constraints (e.g., date range, sport type).</instruction>
    <output>Narrow down to one or more valid candidates that match all conditions (e.g., "bowling", "2009", "Taipei").</output>
  </agent>
  <agent id="4">
    <instruction>Confirm final answer by checking consistency with explicit statements in the context.</instruction>
    <output>Return the unique correct answer that satisfies all criteria from the problem statement.</output>
  </agent>
  <edge from="1" to="2"/>
  <edge from="2" to="3"/>
  <edge from="3" to="4"/>