# Workflow ID: hotpotqa_117_0
# Benchmark: hotpotqa
# Data Indices: [1597, 3611, 3743, 422, 3754]

<agent id="1" type="extract">
        <instruction>Extract the key entities and relationships from the context relevant to the question.</instruction>
    </agent>
    <agent id="2" type="filter">
        <instruction>Filter out irrelevant information based on the extracted entities and focus only on what directly answers the question.</instruction>
    </agent>
    <agent id="3" type="reason">
        <instruction>Reason step-by-step: Identify the film in which Kim Eui-sung stars with Son Ye-jin, then determine its genre based on the context provided.</instruction>
    </agent>
    <agent id="4" type="validate">
        <instruction>Validate that the identified genre matches the description of the film in the context and is consistent across all relevant entries.</instruction>
    </agent>
    <agent id="5" type="output">
        <instruction>Output the final answer as a single string representing the genre of the film.</instruction>
    </agent>
    <connection from="1" to="2"/>
    <connection from="2" to="3"/>
    <connection from="3" to="4"/>
    <connection from="4" to="5"/>