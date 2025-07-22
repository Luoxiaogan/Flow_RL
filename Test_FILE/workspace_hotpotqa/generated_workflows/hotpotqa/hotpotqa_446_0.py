# Workflow ID: hotpotqa_446_0
# Benchmark: hotpotqa
# Data Indices: [883, 1881, 1011, 1180, 51]

<agent id="1">
        <instruction>
            Analyze the given context to identify key entities and their relationships. Focus on extracting structured information that can help answer the question.
        </instruction>
        <output>Extracted entities and relationships</output>
    </agent>
    
    <agent id="2">
        <instruction>
            Use the extracted entities to determine the category or classification of the items in question (e.g., canal, harbor, etc.). Ensure this aligns with the specific query.
        </instruction>
        <output>Category determination</output>
    </agent>
    
    <agent id="3">
        <instruction>
            Verify if both items (Kern Island Canal and Indiana Harbor and Ship Canal) share the same classification based on the context. If yes, return the shared category; otherwise, indicate they differ.
        </instruction>
        <output>Verification result</output>
    </agent>
    
    <agent id="4">
        <instruction>
            Based on the verification, generate a concise answer that directly addresses the question using only the verified category.
        </instruction>
        <output>Final answer</output>
    </agent>
    
    <connection>
        <from>1</from>
        <to>2</to>
    </connection>
    
    <connection>
        <from>2</from>
        <to>3</to>
    </connection>
    
    <connection>
        <from>3</from>
        <to>4</to>
    </connection>