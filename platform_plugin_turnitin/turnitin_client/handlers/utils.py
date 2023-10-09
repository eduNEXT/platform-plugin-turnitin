import json


def pretty_print_response(response, type_of=""):
    """debug helper function"""
    content = response.json()
    print("\n\n")
    print(f"------{type_of}------")
    print("\n\n")
    print(json.dumps(content, indent=4))
    print("\n\n")
    print("------------")
    print("\n\n")
