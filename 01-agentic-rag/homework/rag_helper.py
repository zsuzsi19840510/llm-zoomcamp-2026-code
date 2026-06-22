INSTRUCTIONS = '''
Your task is to answer questions from the course participants
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
'''

PROMPT_TEMPLATE = '''
QUESTION: {question}

CONTEXT:
{context}
'''.strip()


class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        course='llm-zoomcamp',
        filename=None,
        model='gpt-5.4-mini'
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.course = course
        self.prompt_template = prompt_template
        self.filename = filename
        self.model = model
        self.llm_response = None

    def search(self, query, num_results=5):
        #boost_dict = {'content': 2.0}

        #filter_dict = None
        #if self.filename:
        #    filter_dict = {'filename': self.filename}

        return self.index.search(
            query,
            num_results=num_results#,
            #boost_dict=boost_dict,
            #filter_dict=filter_dict
        )

    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append("Content: " + doc['content'])

        return '\n'.join(lines).strip()

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )

    def llm(self, prompt):
        input_messages = [
            {'role': 'developer', 'content': self.instructions},
            {'role': 'user', 'content': prompt}
        ]

        self.llm_response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        return self.llm_response.output_text

    def rag(self, query):
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        answer = self.llm(prompt)

        return answer

    def get_llm_response(self):
        return self.llm_response