# Workflow ID: hotpotqa_267_0
# Benchmark: hotpotqa
# Data Indices: [2977, 1026, 538, 926, 1009]

<operator id="0" type="agent">
        <instruction>Think step by step to determine the correct answer. First, identify the key facts from the context that relate directly to the question. Then, eliminate any irrelevant information. Finally, synthesize the relevant facts to arrive at the correct answer.</instruction>
    </operator>
    <operator id="1" type="agent">
        <instruction>Break down the problem into smaller components. For each component, extract the relevant information from the context. Ensure that each extracted piece of information is accurate and directly addresses part of the question.</instruction>
    </operator>
    <operator id="2" type="agent">
        <instruction>Verify the accuracy of each extracted fact. Cross-reference with other parts of the context if necessary. If a fact contradicts another, resolve the contradiction using logical reasoning or prioritize more specific details.</instruction>
    </operator>
    <operator id="3" type="agent">
        <instruction>Combine all verified facts in a structured manner. Use logical sequencing to ensure the final answer flows coherently from the premises. Avoid introducing new assumptions not supported by the context.</instruction>
    </operator>
    <operator id="4" type="agent">
        <instruction>Double-check your final synthesis against the original question. Confirm that the answer fully addresses what was asked and does not include unnecessary or extraneous information.</instruction>
    </operator>
    <operator id="5" type="agent">
        <instruction>Output only the final answer as a concise statement. Do not include explanations, reasoning steps, or additional commentary.</instruction>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>