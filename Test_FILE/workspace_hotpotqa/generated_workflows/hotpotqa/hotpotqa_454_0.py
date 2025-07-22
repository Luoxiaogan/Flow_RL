# Workflow ID: hotpotqa_454_0
# Benchmark: hotpotqa
# Data Indices: [3807, 2665, 2675, 108]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem. Focus on extracting the main subject, action, and relevant attributes.</instruction>
        <input>problem</input>
        <output>entity_extraction</output>
    </operator>
    <operator id="1">
        <instruction>Based on the extracted entities, determine which agent should process the next step. Consider how each entity connects to the final answer.</instruction>
        <input>entity_extraction</input>
        <output>agent_selection</output>
    </operator>
    <operator id="2">
        <instruction>Process the selected entity using domain-specific knowledge. Ensure all relevant context is applied to derive a precise answer.</instruction>
        <input>agent_selection</input>
        <output>answer_generation</output>
    </operator>
    <operator id="3">
        <instruction>Validate the generated answer against the original context to ensure accuracy and completeness.</instruction>
        <input>answer_generation</input>
        <output>final_answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>