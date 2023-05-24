my_uuid=$(uuidgen)
dist_name="stupid-simple-image-labels-"$my_uuid
pyinstaller app.py --name $dist_name --onefile --add-data "static:static" --add-data "templates:templates"