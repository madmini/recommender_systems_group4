# Assignment 7 / Project

_Note: this file probably looks best in the github.com markdown viewer, which is the recommended viewing platform._

[[_TOC_]]

## Installation

### Fetch project files
```shell script
git clone 
cd recommender_systems_group4/project
```

### (Optionally) create virtual environment

#### Windows
```shell script
python3 -m venv venv
venv\Scripts\activate.bat
```

#### Unix/macOS
```shell script
python3 -m venv venv
source venv/bin/activate
```

### Install required python packages
```shell script
python3 -m pip install -r requirements.txt
```

### (Optionally) add TMDb API-Key
Add API keys to `util/apikeys.secret.json`. This will enable movie poster functionality.

### (Optionally) add a bigger dataset
Per default, only the `ml-latest-small` dataset is included in the repository. 
The project will be able to work that way, but to add value to the user-based approaches,
you may want to add a bigger dataset (e.g. `ml-25m`) to `datasets/`.

More explicit instructions are found in the [datasets readme]( datasets/README_DATASETS.md ).

### Launch server
```shell script
python3 manage.py runserver
```
Note that the first launch may take a longer time as pre-processing (amongst others, building the full text search index) will take place. 

## Structure

### Functional

#### Recommendation Strategies
Code for calculating recommendation scores and helper classes therefore.  
Located in `recommendations/`.

- `adapter.py` functions as the interface to the front end (django), 
  and provides the `recommend_movies(movie_id, method)` function 
  as a simple gateway to all implemented recommendation strategies.
- `method.py` is where recommendation strategies are defined for use in the front end.

Note that this document only covers the scripts that are the base of our strategies.  
For more info on the strategies that made it into our evaluation phase, see the relevant document.

Strategies are mostly implemented as separate scripts in `recommendations/`.   
Frequently used functions were extracted into `recommendations/strategies/shared`.

##### Metrics/Scores
Located in `recommendations/strategies/`.

- `cast_and_crew.py` - using discounted cumulative gain over actors/directors.
- `common_genres.py` - combined approach including filtering for common genres and scoring by user-ratings.
- `meta_mix.py` - combined approach including genre, keywords, actors, directors, release year and production country.
- `tag_genome.py` - promising strategy based on the genome-scores included with `ml-25m`.
  - not included in the evaluation, since due to technical difficulties concerning the implementation, 
    this method was only finished after the feature-freeze for the evaluation phase.
- `tf-idf.py` - TF-IDF over specified columns. Matrix is calculated at server startup.
- `users_who_enjoy_this_also_like.py` - user-based method

###### Dummy strategies
- `dummy.py` - regardless of input, recommend first five movies of dataset.
  - Used for testing the front end, so errors can be properly attributed.
- `reference.py` - outputs TMDb recommendations included in the metadata.  
  - Used in evaluation as closest thing to ground truth available in this case.
- `sequel.py` - direct sequels/prequels.
  - Used to check if filters work correctly.

##### Meta-Strategies
Combine existing strategies to compensate for the drawbacks of single strategies.  
Located in `recommendations/strategies/hybrid`.

- `combined.py` - Linear combination or Product of multiple input scores.
- `slot_based.py` - Assign a number of slots to each input score, 
  output highest scoring movies for each method.

#### Utilities
Various helpers extracted from other scripts that are used throughout the project.  
Located in `util/`.

- `data.py` - Access to datasets. Loaded from disk once, then cached.
  - `data_helper.py` - Various dataset related frequently-used helper functions.
- `search` - Full text search using [whoosh]( https://whoosh.readthedocs.io/en/latest/index.html ).
- `movie_posters.py` - Request movie poster URLs from TMDb or OMDb APIs.
- `exception.py` - Defines project specific exceptions.
- `synchronized.py`, `timer.py` - Function wrappers.

#### Pre-processing
These are scripts that were used to create assets or perform various tasks in advance of actual project execution.
They are technically no longer needed, as they were only they are not referenced in the rest of the project, but are included for archiving purposes.

### Assets
Datasets and search index.  
Located in `datasets/`.

Designed to allow plug-and-play insertion of _movielens-like_ datasets. 
For further info, see our [datasets readme]( datasets/README_DATASETS.md ).

### User Interface

#### Django project
Main django project config.  
Located in `django_main/`.

- `urls.py` - Relays routes to apps.
- `settings.py` - Main config file.

#### Fancy App
The final design for the user interface, created using BootStrap v4.5.0.  
Located in `django_app_fancy/`.

The main element is a heavily modified version of the Carousel component.

##### Logic
- `apps.py` - Contains code that runs on server startup (initialization, pre-loading).
- `urls.py` - Links routes to views.
- `views.py` - Views.

##### Templates (HTML code)
The HTML part of the pages is contained in `django_app_fancy/templates/movie` and has a modular structure.

- `base.html` - Boilerplate HTML. Includes *`footer.html`* and *`static.html`*.
- `footer.html` - Contains the [contractually obligated TMDb reference]( https://www.themoviedb.org/documentation/api/terms-of-use ).
- `static.html` - Include tags for CSS and JS.
- `recommendations.html` - Main template based on the Carousel component. Extends *`base.html`*. Includes *`header.html`*, *`movie_info_item.html`* and *`movie_list_item.html`*.
- `header.html` - The header, containing the title, search bar, and method selection box.
- `movie_info_item.html` - Main item of the Carousel. Based on the Jumbotron component.
- `movie_list_item.html` - Indicators for Carousel items.
- `error.html` - Simple error display page.

#### Old App
The initial simple placeholder UI. Generally the same structure as the fancy new app.  
Located in `django_app_old/`.
