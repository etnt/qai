# Dataset comes from:
#   https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows?resource=download
# It contains (CVS) rows of:
#   Poster_Link,Series_Title,Released_Year,Certificate,Runtime,Genre,IMDB_Rating,Overview,Meta_score,Director,Star1,Star2,Star3,Star4,No_of_Votes,Gross
import argparse
import csv
from qutils import VectorStore, print_verbose, Spinner

template="""
Title: {title}
Rating: {rating}
Genre: {genre}
Starring: {starring}
Story: {story}
"""


def parse_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data


def genres():
    return {'Animation', 'Music', 'Family', 'Sci-Fi', 'Musical', 'Drama', 'Thriller',
        'Action', 'Crime', 'Fantasy', 'War', 'Mystery', 'Western', 'Romance',
        'Comedy', 'History', 'Adventure', 'Sport', 'Biography', 'Film-Noir', 'Horror'}


def main() -> None:
    # Default directory where to store the VectorStore DB
    default_persist_directory = "qimdb"

    # Default location of the CSV file
    default_csv_file = "./data/imdb_top_1000.csv"

    # Default number of results
    default_num_of_results = 3

    genre_set = genres()
    genre_help_text = "Genre of the movie. Possible values are: " + ", ".join(genre_set)

    parser = argparse.ArgumentParser(description='Search for similar Movies')
    parser.add_argument('--title', type=str, help='Title of the movie')
    parser.add_argument('--genre', type=str, help=genre_help_text)
    parser.add_argument('--rating', type=str, help='IMDB rating of the movie')
    parser.add_argument('--stars', type=str, help='Stars of the movie (separated by comma)')
    parser.add_argument('--director', type=str, help='Director of the movie')
    parser.add_argument('--release-year', type=str, help='Release year of the movie')
    parser.add_argument('--story', type=str, help='Story of the movie')
    parser.add_argument('--db-dir', type=str, help='Directory where to store the VectorStore DB')
    parser.add_argument('--csv-file', type=str, help='Location of CSV file')
    parser.add_argument('--num-of-results', type=int, help='Number of returned results')

    args = parser.parse_args()

    if args.genre and args.genre not in genre_set:
        print(f"Error: Invalid genre '{args.genre}'. Use --help to see valid genres.")
        exit(1)

    # Parse the CSV file
    csv_file = args.csv_file or default_csv_file
    data = parse_csv(csv_file)

    # Format the entries to be stored in the VectorStore DB
    entries = []
    metadatas = []
    ids = []
    #genres = set()
    for index, d in enumerate(data):
        #genre_list = d['Genre'].split(', ')
        #for genre in genre_list:
        #    genres.add(genre)
        e = template.format(
            title = d['Series_Title'],
            rating = d['IMDB_Rating'],
            genre = d['Genre'],
            starring = f"{d['Star1']}, {d['Star2']}, {d['Star3']}",
            story = d['Overview']
        )
        entries.append(e)
        metadatas.append({'poster_link': d['Poster_Link']})
        ids.append(f"id{index}")
 
    # Store the entries in the VectorStore DB
    persist_directory = args.db_dir or default_persist_directory
    v = VectorStore(persist_directory=persist_directory)
    if not v.db:
        print(f"Storing into VectorStore as: {persist_directory}")
        spinner = Spinner()
        spinner.start()
        v.store(entries, metadatas, ids, persist_directory=persist_directory)
        spinner.stop()
    else:
        print(f"Using existing VectorStore at: {persist_directory}")

    # Run the Similarity Search!
    query = template.format(
            title = args.title or "",
            rating = args.rating or "",
            genre = args.genre or "",
            starring = args.stars or "",
            story = args.story or ""
            )
    num_results = args.num_of_results or default_num_of_results
    similarity_result = v.similarity_search(query=query, num_results=num_results)
    search_result = "\n\n".join([result.page_content.strip() for result in similarity_result])

    # Print out the answer!
    print("")
    print(search_result)



if __name__ == "__main__":
    main()

