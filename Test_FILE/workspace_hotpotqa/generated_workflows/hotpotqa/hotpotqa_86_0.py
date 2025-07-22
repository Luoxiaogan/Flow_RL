# Workflow ID: hotpotqa_86_0
# Benchmark: hotpotqa
# Data Indices: [2906, 2868, 3728, 828, 326]

<start/>
    <agent id="1" type="question_analysis">
        <instruction>Break down the question to identify key entities and required information.</instruction>
    </agent>
    <agent id="2" type="context_search">
        <instruction>Search for relevant context that matches the key entities from the question.</instruction>
    </agent>
    <agent id="3" type="entity_extraction">
        <instruction>Extract precise answers from the matched context based on the question's focus.</instruction>
    </agent>
    <agent id="4" type="validation">
        <instruction>Verify the extracted answer against all provided context to ensure accuracy.</instruction>
    </agent>
    <agent id="5" type="output_generation">
        <instruction>Format the final answer clearly, ensuring it directly addresses the original question.</instruction>
    </agent>
    <end/>
    <edge from="start" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="end"/>