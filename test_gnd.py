import requests
from twf.clients.gnd_client import send_gnd_request, parse_gnd_request, search_gnd


def main():
    # Example GND search term
    query = "Schmidt, Marie"  # Replace with a real search term or ID

    print("\n=== Combined Search GND ===")
    try:
        results = search_gnd(query, earliest_birth_year=1900, latest_birth_year=2000, show_empty=False)
        if results:
            print("Search Results:")
            for result in results:
                print(result)
        else:
            print("No search results found.")
    except Exception as e:
        print(f"Search failed: {e}")


if __name__ == "__main__":
    main()

# test test