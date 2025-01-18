# RestaurantRating_Autogen



Dataset format

The food at McDonald's was average, but the customer service was unpleasant. The uninspiring menu options were served quickly, but the staff seemed disinterested and unhelpful.

The food is described as "average", which corresponds to a `food_score` of The customer service is described as "unpleasant", which corresponds to a `customer_service_score` of 2. Therefore, the agent should be able to determine `food_score: 3` and `customer_service_score: 2` for this example review.



![Alt text](C:\Users\Tanvi Sankhyan\OneDrive\Desktop\LLM\LLM Agents\lab01_release-20241106T151003Z-001\lab01_release\image.png)

Restaurant Rating analyser following sequential chats patterns

1. Entry point agent initiate the converstaion, e.g. "May I know how good is "restaurant_name"?
2. Data Fetch agent retreive the restaurant name from the string.
3. Entry point agent then take the restaurant name as a prarmeter and call the registered fetch_restaurant_data method and return a list of all the reviews from the data.
4. The data is then used as a carryover to next chat and as something used by the entrypoint agent to initiate chat in the next converstation.
5. The review nalaysis agent returns all the keywords(awful, horrible, disgusting, bad, unpleasant, offensive, average, uninspiring, forgettable, good, enjoyable, satisfying, awesome, incredible, amazing).
6. The entrypoint agent then call the registerd score_reviews method. Each review has 2 keywords, one as a 'food_score' and the second as "customer_service_score" and the review are score based on the following method

                 - Score 1/5 has one of these adjectives: awful, horrible, or disgusting.
                 - Score 2/5 has one of these adjectives: bad, unpleasant, or offensive.
                 - Score 3/5 has one of these adjectives: average, uninspiring, or forgettable.
                 - Score 4/5 has one of these adjectives: good, enjoyable, or satisfying.
                 - Score 5/5 has one of these adjectives: awesome, incredible, or amazing.
8. the output is used a as carryover for the next chat and the registered function calculate_overall_score method is called using the following method. The score is updated by summing, for each item, the square root of the food score squared times the customer service score, normalized by 1 / (N * sqrt(125)), and scaled by 10.
 




