# Workflow ID: hotpotqa_227_0
# Benchmark: hotpotqa
# Data Indices: [491, 1358, 1834, 2663, 725]

<start>
        <operator id="1" type="agent">
            <instruction>Identify the key elements in the question and determine what information is needed to answer it.</instruction>
        </operator>
        <operator id="2" type="agent">
            <instruction>Search for the relevant context that connects the key elements to the answer.</instruction>
        </operator>
        <operator id="3" type="agent">
            <instruction>Extract the specific detail from the context that directly answers the question.</instruction>
        </operator>
        <operator id="4" type="agent">
            <instruction>Verify that the extracted detail matches the question's requirement (e.g., month, date, or event).</instruction>
        </operator>
        <operator id="5" type="agent">
            <instruction>Ensure the answer is precise and unambiguous based on the evidence.</instruction>
        </operator>
        <operator id="6" type="agent">
            <instruction>Format the final output as a clear and concise response.</instruction>
        </operator>
    </start>
    
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>
    <edge from="4" to="5"/>
    <edge from="5" to="6"/>