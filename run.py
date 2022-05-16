import pickle
import time

from group import generate_group, group_recommendation, aggregate_group_rating
from measures import predictions
from metrics import ndcg_group
from processing import remove_missing_film, get_user_rating_dicts, get_movies_aspect_matrix, \
    compute_similarity

MUR = 0.1
MUG = 0.6
MUA = 0.1
MUD = 0.1

if __name__ == "__main__":
    movielens_data = "100k"
    # read rating data
    ratings = pickle.load(open("data/100k_benchmark_ratings.pkl", "rb"))
    # read films data
    films = pickle.load(open("data/100k_benchmark_films_movielens.pkl", "rb"))
    # remove from ratings the missing films (that were missing info and hence were discarded)
    ratings, films = remove_missing_film(films, ratings)
    # user predict
    train_ratings_dict, compressed_test_ratings_dict, user_movie_ratings = get_user_rating_dicts(ratings, films)
    _, movies_all_genres_matrix = get_movies_aspect_matrix(films, "genre")
    _, movies_all_directors_matrix = get_movies_aspect_matrix(films, "director")
    _, movies_all_actors_matrix = get_movies_aspect_matrix(films, "actors")
    # compute user similarity
    ratings_dict, sims = compute_similarity(train_ratings_dict, films)
    # user prediction
    user_predictions = predictions(MUR, MUG, MUA, MUD, films,
                                   compressed_test_ratings_dict, ratings_dict,
                                   sims, movies_all_genres_matrix,
                                   movies_all_directors_matrix,
                                   movies_all_actors_matrix, movielens_data)
    # generate group
    groups = generate_group(user_predictions.keys())
    group_predictions, group_members_predictions = aggregate_group_rating(films, user_predictions, groups, MUG, MUA,
                                                                          MUD)
    g_rating_t, g_recommendation_t, g_explanation_t = group_recommendation(group_predictions, group_members_predictions,
                                                                           groups, "threshold", 2.5,
                                                                           films, MUG, MUA, MUD)

    g_rating_a, g_recommendation_a, g_explanation_a = group_recommendation(group_predictions, group_members_predictions,
                                                                           groups, "average",
                                                                           2, films, MUG, MUA, MUD)
    group_evaluation = ndcg_group(compressed_test_ratings_dict, groups, g_rating_t, g_recommendation_t, "threshold")
    print(group_evaluation)

    # 0.10146982971243731 group scale=3
    # 0.013707188085947652 group scale=5
