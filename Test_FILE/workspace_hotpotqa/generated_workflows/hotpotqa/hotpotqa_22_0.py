# Workflow ID: hotpotqa_22_0
# Benchmark: hotpotqa
# Data Indices: [2845, 1112, 990, 3284, 962]

<operator id="0">
        <instruction>Identify the key entities and relationships in the problem context to determine what needs to be extracted.</instruction>
        <input>problem</input>
        <output>entities_and_relations</output>
    </operator>
    <operator id="1">
        <instruction>Extract relevant information from the context that directly answers the question. Focus on specific details like names, locations, or attributes.</instruction>
        <input>entities_and_relations</input>
        <output>extracted_info</output>
    </operator>
    <operator id="2">
        <instruction>Validate the extracted information against the question to ensure relevance and correctness.</instruction>
        <input>extracted_info</input>
        <output>validated_info</output>
    </operator>
    <operator id="3">
        <instruction>Generate a concise and accurate answer based on the validated information.</instruction>
        <input>validated_info</input>
        <output>final_answer</output>
    </operator>
    <edge from="0" to="1"/>
    <edge from="1" to="2"/>
    <edge from="2" to="3"/>