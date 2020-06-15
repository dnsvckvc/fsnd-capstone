dropdb okr_test_local
createdb okr_test_local
flask db upgrade
python create_dummy_data.py
python test_okr.py
