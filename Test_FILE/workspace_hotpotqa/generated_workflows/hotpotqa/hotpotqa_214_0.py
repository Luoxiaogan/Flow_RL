# Workflow ID: hotpotqa_214_0
# Benchmark: hotpotqa
# Data Indices: [1179, 1086, 547, 2075, 654]

<operator id="0" type="agent">
        <instruction>Identify the key entities and relationships in the problem statement. Break down the question to understand what specific information is being asked.</instruction>
        <input>problem</input>
        <output>parsed_question</output>
    </operator>
    <operator id="1" type="agent">
        <instruction>Search for all contextual references that might contain the answer. Focus on entities directly related to the question's subject, such as companies, locations, or events mentioned in the context.</instruction>
        <input>context</input>
        <output>relevant_context</output>
    </operator>
    <operator id="2" type="agent">
        <instruction>Extract the location associated with the company that used Leavitt Farm as headquarters and museum facility. Cross-reference this with the parsed question to ensure accuracy.</instruction>
        <input>relevant_context</input>
        <output>location</output>
    </operator>
    <operator id="3" type="agent">
        <instruction>Verify the extracted location by checking if it matches any known city, state, or region from the context. Ensure no misinterpretation of names or places occurs.</instruction>
        <input>location</input>
        <output>verified_location</output>
    </operator>
    <operator id="4" type="agent">
        <instruction>Finalize the answer by confirming the location is consistent with both the question and the provided context. Return only the verified location as the final output.</instruction>
        <input>verified_location</input>
        <output>final_answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>
    <edge from="3" to="4"/>