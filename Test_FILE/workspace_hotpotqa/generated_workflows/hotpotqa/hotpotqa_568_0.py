# Workflow ID: hotpotqa_568_0
# Benchmark: hotpotqa
# Data Indices: [1735, 2782, 142, 3296]

<agent name="Extractor">
        <instruction>Identify key entities and relationships from the context relevant to the question. Focus on names, dates, and connections between people, works, and events.</instruction>
        <input>problem</input>
        <output>entities_and_relations</output>
    </agent>

    <agent name="Mapper">
        <instruction>Map extracted entities to known facts or categories (e.g., songwriter → birth year, actor → film role). Ensure each entity is linked to its correct attribute.</instruction>
        <input>entities_and_relations</input>
        <output>mapped_data</output>
    </agent>

    <agent name="Validator">
        <instruction>Verify consistency of mapped data against all provided context. Eliminate contradictions or ambiguous links that do not align with the problem’s constraints.</instruction>
        <input>mapped_data</input>
        <output>validated_data</output>
    </agent>

    <agent name="Resolver">
        <instruction>Use validated data to directly answer the question. If multiple candidates exist, apply logical filtering based on specificity and uniqueness in the context.</instruction>
        <input>validated_data</input>
        <output>final_answer</output>
    </agent>

    <connect from="Extractor" to="Mapper"/>
    <connect from="Mapper" to="Validator"/>
    <connect from="Validator" to="Resolver"/>