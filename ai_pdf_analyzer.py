from openai import OpenAI

class AIClient:
    def __init__(self, api_key, base_url="https://openrouter.ai/api/v1"):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.system_message = """
            You are a tool that helps me identify juridical cases with modern slavery accusations. You will be important to the creation of a database containing information of various \
            cases so I can train an NLP Model and identify other human exploitation and develop my master's thesis tool that will help society identify and stop future cases.
        """

    def generate_prompt(self, text, topic):
        prompt = f"""
            This case was found in the Canadian organization CanLII. \
            It contains the sentence "{topic}" at least once throughout its content. \
            You should analyze whether the case is about {topic} or if it's just a mention of the term. \
            I need you to help me identify if this case is related to Modern Slavery or not. 
            
            Here is a segment of the PDF available on the CanLII website:

            {text}

            ----

            Instructions for task completion:
            - Read the and analyze the document provided.
            - Your output should only be a boolean value (True or False) indicating if the case is related to {topic} or not.
            - DO NOT include anything else in your output.
            """
        return prompt

    def analyze_text(self, text, topic):
        prompt = self.generate_prompt(text, topic)
        completion = self.client.chat.completions.create(
            model="deepseek/deepseek-chat:free",
            messages=[
                {
                    "role": "system",
                    "content": self.system_message
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content