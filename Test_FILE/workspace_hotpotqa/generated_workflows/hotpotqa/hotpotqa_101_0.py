# Workflow ID: hotpotqa_101_0
# Benchmark: hotpotqa
# Data Indices: [2894, 2752, 2631, 493, 1324]

<start/>
    <agent id="1" type="question_analysis">
        <instruction>Break down the question to identify key entities and what needs to be determined.</instruction>
    </agent>
    <agent id="2" type="context_retrieval">
        <instruction>Extract relevant information from the context that directly answers the question.</instruction>
    </agent>
    <agent id="3" type="comparison_logic">
        <instruction>Compare the relevant data points to determine the correct answer based on the question's requirement.</instruction>
    </agent>
    <agent id="4" type="verification">
        <instruction>Double-check the comparison logic against the context to ensure accuracy.</instruction>
    </agent>
    <agent id="5" type="final_answer">
        <instruction>Formulate the final answer clearly based on verified results.</instruction>
    </agent>
    <end/>
    <edge from="start" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="end"/>