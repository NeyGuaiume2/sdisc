import os

# Arquivo antigo -> arquivo novo
renames = {
    "backend/models/disc-result.py": "backend/models/disc_result.py",
    "backend/static/images/favicon-16.ico": "backend/static/images/favicon_16.ico",
    "backend/static/images/favicon-32.ico": "backend/static/images/favicon_32.ico",
    "backend/static/images/favicon-48.ico": "backend/static/images/favicon_48.ico",
    "backend/static/images/favicon-64.ico": "backend/static/images/favicon_64.ico",
    "backend/static/js/disc_questions.js": "backend/static/js/disc_questions.js",  # Já está com underscore
    "backend/static/js/disc_quiz.js": "backend/static/js/disc_quiz.js", # Já está com underscore
    "backend/static/js/disc_scoring.js": "backend/static/js/disc_scoring.js",  # Já está com underscore
    "tests/test_disc_scoring.py": "tests/test_disc_scoring.py", # Já está com underscore
    "tests/integration-tests.py": "tests/integration_tests.py"
}

for old_name, new_name in renames.items():
    try:
        os.rename(old_name, new_name)
        print(f"Renamed '{old_name}' to '{new_name}'")
    except FileNotFoundError:
        print(f"File not found: '{old_name}'")
    except FileExistsError:
        print(f"File already exists: '{new_name}'")
    except Exception as e:
        print(f"Error renaming '{old_name}': {e}")