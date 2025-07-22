# Workflow ID: hotpotqa_455_0
# Benchmark: hotpotqa
# Data Indices: [1830, 1397, 2248, 2316]

<operator id="0" type="reasoning">
        <instruction>Identify the primary indigenous Romance language spoken on most of the island of Sardinia by analyzing the context provided.</instruction>
        <input>context</input>
        <output>language</output>
    </operator>
    <operator id="1" type="verification">
        <instruction>Confirm that the identified language matches the description of being the closest genealogical descendant to Latin among Romance languages and is primarily spoken in Sardinia.</instruction>
        <input>language, context</input>
        <output>verified_language</output>
    </operator>
    <operator id="2" type="classification">
        <instruction>Determine if the verified language belongs to the Romance language family and is indigenous to Sardinia based on linguistic classification criteria.</instruction>
        <input>verified_language, context</input>
        <output>classification_result</output>
    </operator>
    <operator id="3" type="final_check">
        <instruction>Ensure the final output correctly identifies the language as Sardinian, which is known for its close relationship to Latin and its status as the primary indigenous Romance language in Sardinia.</instruction>
        <input>classification_result</input>
        <output>final_answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>