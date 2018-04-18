# Purpose: process a listed ingredient into subset of primarily three pieces of data: ingredient, quantity, unit
# Possibly categorize rest of listed item as "miscellaneous"
# 
# Considerations:
#   Without a massive ingredients database, much of the ingredients will not be identifiable. It may be possible to infer where the ingredients are
#   located based on the relative positioning of tokens within a listed item. Some clues may be the usage of non-alphanumerics such as '(', ')', ',', ':', '-'
#   
#   for example: paprika - 10 ounces
#                paprika, 10 ounces
#   
#   token before the non-alphanumeric characters IS the ingredient
# 
#
# Strategies:
#   a. Tokenization using non-alphanumerics as delimiter
#       1. tokenize list
#       2. classify tokens using regex
#       3. bundle data together based on relative positioning of classified tokens
#   
#   rules used:if there are no tokens between a pair of (quantity + unit), they are associated with the same ingredient
#   
#   Example: 1 bunch (10oz) of spinach
#   Tokens: ["1", "bunch", "10oz", "of", "spinach"]
#   classified: quantity, unit, quantity, unit, misc, ? or ingredient (based on what the database contains)
#   bundling of data:  1 bunch / 10oz spinach
#
#   CONSIDER THIS: non-alphanumeric delimiters are being removed in this approach. Maybe the locations should be noted in cases the 
#                   positioning of ingredients may need to be guessed when database does not contain the ingredient
#
#
#
