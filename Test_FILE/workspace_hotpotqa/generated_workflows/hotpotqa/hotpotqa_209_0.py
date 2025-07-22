# Workflow ID: hotpotqa_209_0
# Benchmark: hotpotqa
# Data Indices: [3231, 3417, 1446, 1058, 3848]

<agent id="1">
    <instruction>Identify the key elements in the question and context that relate to the film referenced in the cover art.</instruction>
    <output>Extract the phrase "Luck of the Corpse" and note its connection to a film's cover art.</output>
  </agent>
  <agent id="2">
    <instruction>From the context, locate which film's cover art is used for "Luck of the Corpse".</instruction>
    <output>Find that the cover art is from the 1963 film "Black Sabbath".</output>
  </agent>
  <agent id="3">
    <instruction>Determine who directed "Black Sabbath".</instruction>
    <output>Identify Mario Bava as the director of "Black Sabbath".</output>
  </agent>
  <agent id="4">
    <instruction>Verify that no other films or directors are ambiguously linked to the cover art.</instruction>
    <output>Confirm that only "Black Sabbath" is cited in the context as the source of the cover art.</output>
  </agent>
  <agent id="5">
    <instruction>Compile the final answer by linking the film to its director.</instruction>
    <output>Mario Bava directed the film "Black Sabbath", whose cover art was used for "Luck of the Corpse".</output>
  </agent>
  <connection from="1" to="2"/>
  <connection from="2" to="3"/>
  <connection from="3" to="5"/>
  <connection from="4" to="5"/>