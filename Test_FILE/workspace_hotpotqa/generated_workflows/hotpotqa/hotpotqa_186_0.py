# Workflow ID: hotpotqa_186_0
# Benchmark: hotpotqa
# Data Indices: [3686, 1698, 1364, 2327]

<operator id="0">
        <instruction>Identify the key entities in the problem and determine which one directly answers the question.</instruction>
        <input>problem</input>
        <output>entity_candidates</output>
    </operator>
    <operator id="1">
        <instruction>For each candidate, verify if it matches the exact criteria stated in the question using contextual evidence from the provided text.</instruction>
        <input>entity_candidates</input>
        <output>verified_matches</output>
    </operator>
    <operator id="2">
        <instruction>Filter out any candidates that do not have sufficient supporting evidence or are ambiguous in context.</instruction>
        <input>verified_matches</input>
        <output>final_candidates</output>
    </operator>
    <operator id="3">
        <instruction>Among the final candidates, select the one that best satisfies the question's requirement based on direct textual support.</instruction>
        <input>final_candidates</input>
        <output>answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>