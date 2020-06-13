# Assignment 7 / Project

_Note: this file probably looks best in the github.com markdown viewer, which is the recommended viewing platform._

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

### Launch server
```shell script
python3 manage.py runserver
```
Note that the first launch may take a longer time as, pre-processing (amongst others, building the full text search index) will take place. 

## Structure

### Functional

#### Recommendation Strategies
Code for calculating recommendation scores and helper classes therefore.  
Located in `recommendations/`.

`adapter.py` functions as the interface to the front end (django), and provides the `recommend_movies(movie_id, method)` function as a simple gateway to all implemented recommendation strategies.

Strategies are implemented as separate scripts in `recommendations/`. 
To be included in the main program, each strategy has to be included in the `Method` enum in `adapter.py`.

Strategies include

- TODO 

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
They are technically no longer needed, as they are not referenced in the rest of the project, but are included for archiving purposes.

### Assets
Datasets and search index.  
Located in `datasets/`.

Designed to allow plug-and-play insertion of _movielens-like_ datasets.

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

#### Old App
The initial simple placeholder UI. Generally the same structure as the fancy new app.  
Located in `django_app_old/`.
