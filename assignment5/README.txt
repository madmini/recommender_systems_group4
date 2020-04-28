Solutions for Assignment 5.

Scripts:

    movielens.py - adapter for this dataset, create dataframes from the files in ml-1m/
    recommender.py - recommender system logic
    main.py - accumulates test results and outputs them as csv and png plots

Assets:

    ml-1m/* - the dataset

Results:

    results.png - metrics plotted over neighborhood size (k)
                  the results suggest that increasing the neighborhood size beyond a certain point does not yield any benefits
                  and can even harm the quality of the recommendations