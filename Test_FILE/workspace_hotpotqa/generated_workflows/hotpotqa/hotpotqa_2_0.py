# Workflow ID: hotpotqa_2_0
# Benchmark: hotpotqa
# Data Indices: [3919, 407, 1865, 286]

<agent id="1" type="reasoning">
        <instruction>Identify the key entities and relationships in the context to determine the nationality of the person whose music inspired the Folias Flute and Guitar Duo.</instruction>
        <input>context</input>
        <output>person_inspired</output>
    </agent>
    <agent id="2" type="lookup">
        <instruction>Determine the nationality of the person identified in the previous step based on their biographical details.</instruction>
        <input>person_inspired</input>
        <output>nationality</output>
    </agent>
    <agent id="3" type="validation">
        <instruction>Verify that the nationality derived from the lookup matches the context's description of the inspiration source.</instruction>
        <input>nationality, context</input>
        <output>valid</output>
    </agent>
    <agent id="4" type="final_answer">
        <instruction>Provide the final answer based on the validated nationality.</instruction>
        <input>valid</input>
        <output>answer</output>
    </agent>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>