def user_preferences(content):
    """
    content = {
        "message": "write me a post about social media",
        "approximate_words": num,
        "hashtags": bool,
        "emojis": bool,
        "required_words": [string],
        "forbidden_words": [string]
    }
    """
    message = f"{content['message']} and make it around {content['approximate_words']} words."

    if content['emojis']:
        message += " Add relevant emojis naturally to the description."

    if content['required_words']:
        message += f" Make sure to include these words in the description: {', '.join(content['required_words'])}."

    if content['forbidden_words']:
        message += f" Avoid using these words: {', '.join(content['forbidden_words'])}."
    
    if content['hashtags']:
        message += "Use 5–7 relevant, niche-specific hashtags that increase discoverability and avoid generic ones. Place them only at the end of the description, on a new line, without mixing them into the main text."

    return message
