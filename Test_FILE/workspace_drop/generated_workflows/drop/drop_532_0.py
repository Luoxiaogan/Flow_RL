# Workflow ID: drop_532_0
# Benchmark: drop
# Data Indices: [1262, 0, 2684, 3211, 2165]

<operator id="1">
    <instruction>
      Analyze the input to identify key numerical or categorical data relevant to the question. Break down the passage into structured components such as teams, players, scores, and events.
    </instruction>
    <input>problem</input>
    <output>structured_data</output>
  </operator>

  <operator id="2">
    <instruction>
      Extract all instances of the specific entity mentioned in the question (e.g., touchdowns, companies, sons) from the structured data. Organize them by context, such as time (first half, second half), position, or role.
    </instruction>
    <input>structured_data</input>
    <output>filtered_entities</output>
  </operator>

  <operator id="3">
    <instruction>
      If the question involves comparison or ranking (e.g., longest/shortest pass, more than), sort the extracted entities based on the relevant metric (e.g., yardage, count). Ensure ties are handled appropriately.
    </instruction>
    <input>filtered_entities</input>
    <output>sorted_entities</output>
  </operator>

  <operator id="4">
    <instruction>
      Identify the exact answer by locating the value or item that matches the question's requirement (e.g., third longest, difference in counts, name of a person).
    </instruction>
    <input>sorted_entities</input>
    <output>final_answer</output>
  </operator>

  <operator id="5">
    <instruction>
      Validate the final answer against the original passage to ensure correctness and avoid misinterpretation due to ambiguous phrasing or missing context.
    </instruction>
    <input>final_answer</input>
    <input>problem</input>
    <output>validated_answer</output>
  </operator>

  <operator id="6">
    <instruction>
      Format the validated answer into a concise, clear response that directly answers the question without additional explanation.
    </instruction>
    <input>validated_answer</input>
    <output>formatted_output</output>
  </operator>

  <connection>
    <from>1</from>
    <to>2</to>
  </connection>
  <connection>
    <from>2</from>
    <to>3</to>
  </connection>
  <connection>
    <from>3</from>
    <to>4</to>
  </connection>
  <connection>
    <from>4</from>
    <to>5</to>
  </connection>
  <connection>
    <from>5</from>
    <to>6</to>
  </connection>