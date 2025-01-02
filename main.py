from typing import Dict, List
from autogen import ConversableAgent
import sys
import os
import numpy as np
from typing import Dict, List
from autogen import register_function

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    
    with open('restaurent-data.txt', 'r') as file:
        content=file.read()
        print(content)

    data_dict:Dict[str, List[str]] = {}
    entries= content.split('\n')

    for entry in entries:
        if '.' in entries:
            key, value = entry.split('.',1)
            key - key.strip()
            value = value.strip()
            
            if key in data_dict:
                data_dict[key].append(value)

            else:
                data_dict[key] = value
            
    return {restaurant_name: data_dict[restaurant_name]} if restaurant_name in data_dict else{}
    



def score_reviews(input_dict: Dict[str, List[str]]) -> str:
    score_dict: Dict[int, List[str]] = {
        1: ["awful", "horrible", "disgusting"],
        2: ["bad", "unpleasant", "offensive"],
        3: ["average", "uninspiring", "forgettable"],
        4: ["good", "enjoyable", "satisfying"],
        5: ["awesome", "incredible", "amazing"]
    }

    def get_score(review: str) -> int:
        """Assign a score to a review based on predefined adjectives."""
        for score, adjectives in score_dict.items():
            if review in adjectives:
                return score
        return 0  # Default score if no match is found

    output_str = ""

    for restaurant, reviews in input_dict.items():
        # Ensure reviews are paired correctly, and handle uneven lists
        food_reviews: List[str] = reviews[::2]  # Reviews for food (even indices)
        customer_reviews: List[str] = reviews[1::2]  # Reviews for customer service (odd indices)

        food_scores: List[int] = [get_score(review) for review in food_reviews]
        customer_scores: List[int] = [get_score(review) for review in customer_reviews]

        # Correctly pair scores to avoid unaligned results
        output_str += f'"{restaurant}", {food_scores}, {customer_scores}'

    return output_str


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
   
    N=len(food_scores)

    score=0
    score += sum(np.sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * np.sqrt(125)) * 10
                 for i in range(N)
        )

    return{restaurant_name: score}
   
    


# Do not modify the signature of the "main" function.
def main(user_query: str):
    entrypoint_agent_system_message = "You are an entry point agent. If the information passed is a Review, then pass the name of the resurent. If the information passed is the Python dictionary where values are the list of string, then find the food score and custormer service score. If the information passed is the python dictionary where the values are list of integers, then find the overall score." # TODO
    # example LLM config for the entrypoint agent
    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}
    # the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config)
    entrypoint_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)
    entrypoint_agent.register_for_llm(name="score_reviews", description="Score Reviews for a specific restaurant")(score_reviews)
    entrypoint_agent.register_for_execution(name="score_reviews")(score_reviews)
    #to calculate_overall_score function
    entrypoint_agent.register_for_llm(name="calculate_overall_score", description="Calculate Overall Score for the restaurant")(calculate_overall_score)
    entrypoint_agent.register_for_execution(name="calculate_overall_score")(calculate_overall_score)


    # TODO
    # Agent 2
    datafetch = ConversableAgent(
        name="Data Fetch Agent",
        system_message="You are a helpful AI assistant. "
        "You are a data fetch agent which retreives the name of the restuarent and returns just the name in "" double quotes "
        "Return the content (reviews or data) when the task is done as recieved from the function as python dictionary without removing anything, not just the name.",
        llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]},
        )

    # Agent 3
    reviewanalysis = ConversableAgent(
        name="Review Analysis Agent",
        system_message="You are a helpful AI assistant. "
        "You are a review analysis which looks for all the keywords(awful, horrible, disgusting, bad, unpleasant, offensive, average, uninspiring, forgettable, good, enjoyable, satisfying, awesome, incredible, amazing) in the keys of the dictionary and just keep them in the keys of the dictionary in same order you find them. Remeber that the number od food score are equal to the number of customer service review. Dont loose any data "
        "Return the results as recieved from the function when the task is done and dont return the list of keywords",
        llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]},
        )

    scoringagent = ConversableAgent(
        name="Scoring Agent",
        system_message="You are a helpful AI assistant. "
        "You are given a dictionary where restaurant name is a key and value being comma-separated list of food score and customer serice score. I want you to keep just the second dictionary "
        "Return the results upto three decimal places when the task is done",
        llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]},
        )
    
    register_function(
        fetch_restaurant_data,
        caller=datafetch,  # The assistant agent can suggest calls to the calculator.
        executor=entrypoint_agent,  # The user proxy agent can execute the calculator calls.
        name="fetch_restaurant_data",  # By default, the function name is used as the tool name.
        description="Fetching Restaurant Data",  # A description of the tool.
    )

    register_function(
        score_reviews,
        caller=reviewanalysis,  
        executor=entrypoint_agent,  
        name="score_reviews",  
        description="Score Reviews", 
    )

    register_function(
        calculate_overall_score,
        caller=scoringagent,  
        executor=entrypoint_agent,  
        name="calculate_overall_score",  
        description="Calculate Overall Score",  
    )
    
    # Fill in the argument to `initiate_chats` below, calling the correct agents sequentially.
    result = entrypoint_agent.initiate_chats(
        [
            {
                "recipient": datafetch,
                "message": user_query,
                "max_turns": 2,
                "summary_method": "last_msg",
            },
            {
                "recipient": reviewanalysis,
                "message": "Here are the reviews?",
                "max_turns": 3,
                "summary_method": "last_msg",
            },
            {
                "recipient": scoringagent,
                "message": "Score the reviews",
                "max_turns": 2,
                "summary_method": "last_msg",
            },

        ]
    )
    # Uncomment once you initiate the chat with at least one agent.
    # result = entrypoint_agent.initiate_chats([{}])
    
# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "What do you think about Panera Bread?"
    main(sys.argv[1])